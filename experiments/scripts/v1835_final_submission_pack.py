#!/usr/bin/env python3
"""Build the final HW2 submission/report package from validated candidates.

This utility copies selected CSV candidates, writes manifests, drafts the
assignment-facing Markdown reports, and runs local validation/lint checks.  It
never uploads to Kaggle and never calls external services.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent

STUDENT_ID = "D13922024"
DATE = "2026-05-14"
DEADLINE = "2026-05-15 23:59"
BASELINE_PRIVATE = 0.47119
TOP3_THRESHOLD = 0.50671
DEFAULT_OUT = Path("experiments/final_submission_package")
VALIDATOR = Path("werewolf-project/assert/validate_submission.py")


@dataclass(frozen=True)
class CandidateSpec:
    group: str
    order: int
    candidate: str
    lane: str
    source: Path
    dest_name: str
    private_score: str
    condition: str
    rationale: str


QUEUE: tuple[CandidateSpec, ...] = (
    CandidateSpec(
        group="queue",
        order=1,
        candidate="v1826a",
        lane="primary_first",
        source=Path("experiments/submissions/submission_v1826a_g4_g29_apboost_push_private.csv"),
        dest_name="01_v1826a_primary_first_private.csv",
        private_score="pending",
        condition="Upload first in the normal final-attempt sequence.",
        rationale="g4/g29 exact white contradictions plus limited AP boosts; best evidence/risk balance in the new queue.",
    ),
    CandidateSpec(
        group="queue",
        order=2,
        candidate="v1826b",
        lane="if_01_positive",
        source=Path("experiments/submissions/submission_v1826b_g4_g29_g23_joachim_push_private.csv"),
        dest_name="02_v1826b_if_01_positive_private.csv",
        private_score="pending",
        condition="Use if v1826a improves or gives a positive signal.",
        rationale="Adds the g23 Joachim structural repair to the g4/g29 core for higher upside.",
    ),
    CandidateSpec(
        group="queue",
        order=3,
        candidate="v1826d",
        lane="if_02_positive",
        source=Path("experiments/submissions/submission_v1826d_g4_g29_g23_apboost_push_private.csv"),
        dest_name="03_v1826d_if_02_positive_private.csv",
        private_score="pending",
        condition="Use if v1826b improves over v1826a.",
        rationale="v1826b plus AP boosts; best only after the shared direction is confirmed.",
    ),
    CandidateSpec(
        group="queue",
        order=4,
        candidate="v1826c",
        lane="alt_structural",
        source=Path("experiments/submissions/submission_v1826c_g4_g29_g6_dualwhite_push_private.csv"),
        dest_name="04_v1826c_alt_structural_private.csv",
        private_score="pending",
        condition="Use if still below the top-3 threshold and testing the g6 structural lane is acceptable.",
        rationale="Alternative structural branch with higher uncertainty than v1826a/b/d.",
    ),
    CandidateSpec(
        group="queue",
        order=5,
        candidate="v1829e",
        lane="clean_hailmary",
        source=Path("experiments/submissions/submission_v1829e_v1826d_plus_g17_g27_cleaner_hailmary_private.csv"),
        dest_name="05_v1829e_clean_hailmary_private.csv",
        private_score="pending",
        condition="Preferred final-slot attempt if earlier queue entries are positive but still below top-3.",
        rationale="Cleaner high-upside final attempt: v1826d plus g17/g27, avoiding the noisiest all-in additions.",
    ),
)

KNOWN_BEST: tuple[CandidateSpec, ...] = (
    CandidateSpec(
        group="known_best",
        order=1,
        candidate="v1824a",
        lane="verified_best",
        source=Path("experiments/submissions/submission_v1824a_v1823a_plus_g24_thomas_trueseer_private.csv"),
        dest_name="01_v1824a_score_0p47119_private.csv",
        private_score="0.47119",
        condition="Current best verified private score; keep as rollback/final if no new attempt improves.",
        rationale="v1823a plus g24 Thomas true-Seer repair; highest user-reported private score so far.",
    ),
    CandidateSpec(
        group="known_best",
        order=2,
        candidate="v1823a",
        lane="verified_second_tie",
        source=Path("experiments/submissions/submission_v1823a_v1821a_plus_v1819b_positive_stack_private.csv"),
        dest_name="02_v1823a_score_0p46492_private.csv",
        private_score="0.46492",
        condition="Known positive stack backup.",
        rationale="v1821a plus v1819b positive stack; tied second among known verified scores.",
    ),
    CandidateSpec(
        group="known_best",
        order=3,
        candidate="v1823b",
        lane="verified_second_tie_alt",
        source=Path("experiments/submissions/submission_v1823b_v1821a_v1819b_plus_g30_dieter_private.csv"),
        dest_name="03_v1823b_score_0p46492_private.csv",
        private_score="0.46492",
        condition="Alternative tied backup with g30 Dieter branch.",
        rationale="Same verified private score as v1823a; useful for audit and rollback comparison.",
    ),
    CandidateSpec(
        group="known_best",
        order=4,
        candidate="v1821a",
        lane="verified_fourth",
        source=Path("experiments/submissions/submission_v1821a_claimgraph_g10_pamela_repair_private.csv"),
        dest_name="04_v1821a_score_0p46455_private.csv",
        private_score="0.46455",
        condition="Stable claim-graph repair baseline.",
        rationale="Claim-graph CSP plus g10 Pamela repair; close to the v1823 stack score.",
    ),
    CandidateSpec(
        group="known_best",
        order=5,
        candidate="v1819b",
        lane="verified_fifth",
        source=Path("experiments/submissions/submission_v1819b_v1817b_v1818a_private.csv"),
        dest_name="05_v1819b_score_0p45499_private.csv",
        private_score="0.45499",
        condition="Conservative older high-score backup.",
        rationale="v1817b/v1818a stack; fifth among current known verified private results.",
    ),
)

KNOWN_BEST_OVERLAY: tuple[CandidateSpec, ...] = (
    CandidateSpec(
        group="known_best_overlay",
        order=1,
        candidate="v1845a",
        lane="v1824a_strict_ap_overlay",
        source=Path("experiments/submissions/submission_v1845a_v1824a_strict_ap_overlay_private.csv"),
        dest_name="01_v1845a_v1824a_strict_ap_overlay_private.csv",
        private_score="pending",
        condition="Score-only fallback on verified-best v1824a if structural role changes are considered too risky.",
        rationale="Preserves v1824a roles and applies strict high-precision AP demotes/boosts only.",
    ),
    CandidateSpec(
        group="known_best_overlay",
        order=2,
        candidate="v1845b",
        lane="v1824a_medium_ap_overlay",
        source=Path("experiments/submissions/submission_v1845b_v1824a_medium_ap_overlay_private.csv"),
        dest_name="02_v1845b_v1824a_medium_ap_overlay_private.csv",
        private_score="pending",
        condition="Score-only fallback on v1824a with the v1840 Medium-result agree-direction gate.",
        rationale="Preserves v1824a roles; public proxy is close to v1841 without structural interaction risk.",
    ),
    CandidateSpec(
        group="known_best_overlay",
        order=3,
        candidate="v1845c",
        lane="v1824a_blackboost_score_overlay",
        source=Path("experiments/submissions/submission_v1845c_v1824a_blackboost_score_overlay_private.csv"),
        dest_name="03_v1845c_v1824a_blackboost_score_overlay_private.csv",
        private_score="pending",
        condition="Maximum public-proxy score-only fallback on verified-best v1824a.",
        rationale="Preserves v1824a roles while adding baseline-Seer black disagreement AP boosts.",
    ),
)

CONTINGENCY: tuple[CandidateSpec, ...] = (
    CandidateSpec(
        group="contingency",
        order=1,
        candidate="v1825c",
        lane="diagnostic_neutral",
        source=Path("experiments/submissions/submission_v1825c_g4_g29_combo_private.csv"),
        dest_name="01_v1825c_diagnostic_neutral_private.csv",
        private_score="pending",
        condition="Use if v1826a is near-neutral and the AP boost layer needs isolation.",
        rationale="Clean g4+g29 diagnostic without AP boosts.",
    ),
    CandidateSpec(
        group="contingency",
        order=2,
        candidate="v1825a",
        lane="diagnostic_mild_regression",
        source=Path("experiments/submissions/submission_v1825a_g4_regina_white_repair_private.csv"),
        dest_name="02_v1825a_diagnostic_mild_regression_private.csv",
        private_score="pending",
        condition="Use if v1826a mildly regresses but the g4 isolate remains worth testing.",
        rationale="Clean g4 isolate for regression diagnosis.",
    ),
    CandidateSpec(
        group="contingency",
        order=3,
        candidate="v1827a",
        lane="fallback_severe_regression",
        source=Path("experiments/submissions/submission_v1827a_g17_simon_black_repair_private.csv"),
        dest_name="03_v1827a_fallback_severe_regression_private.csv",
        private_score="pending",
        condition="Use if v1826a severely regresses and the g4/g29 family should be abandoned.",
        rationale="Disjoint g17 Simon black repair fallback.",
    ),
    CandidateSpec(
        group="contingency",
        order=4,
        candidate="v1827d",
        lane="fallback_after_positive_then_negative",
        source=Path("experiments/submissions/submission_v1827d_v1826a_plus_g17_simon_black_private.csv"),
        dest_name="04_v1827d_after_v1826a_positive_b_negative_private.csv",
        private_score="pending",
        condition="Use if v1826a improves but v1826b regresses or is neutral.",
        rationale="v1826a plus disjoint g17 repair.",
    ),
    CandidateSpec(
        group="contingency",
        order=5,
        candidate="v1826e",
        lane="standard_allin",
        source=Path("experiments/submissions/submission_v1826e_allin_g4_g29_g23_g6_ap_g5_private.csv"),
        dest_name="05_v1826e_standard_allin_private.csv",
        private_score="pending",
        condition="Use only if avoiding g17/g27 residues is preferred over the cleaner Hail Mary queue file.",
        rationale="Original all-in stack, including the noisier g6/g5 additions.",
    ),
    CandidateSpec(
        group="contingency",
        order=6,
        candidate="v1829d",
        lane="maximum_allin",
        source=Path("experiments/submissions/submission_v1829d_v1826e_plus_g17_g27_g18_private.csv"),
        dest_name="06_v1829d_maximum_allin_private.csv",
        private_score="pending",
        condition="Use only as a true final-slot maximum-risk attempt.",
        rationale="Maximum-upside all-in candidate with the highest regression risk.",
    ),
)

OVERLAY: tuple[CandidateSpec, ...] = (
    CandidateSpec(
        group="overlay",
        order=1,
        candidate="v1838a",
        lane="v1826a_confirmed_white_overlay",
        source=Path("experiments/submissions/submission_v1838a_v1826a_confirmed_white_overlay_private.csv"),
        dest_name="01_v1838a_v1826a_confirmed_white_overlay_private.csv",
        private_score="pending",
        condition="Optional replacement for queue order 1 if accepting the confirmed-white AP demote overlay.",
        rationale="v1826a plus g26 Simon confirmed-white score demote; public counterpart improves AP slightly.",
    ),
    CandidateSpec(
        group="overlay",
        order=2,
        candidate="v1838b",
        lane="v1826d_confirmed_white_overlay",
        source=Path("experiments/submissions/submission_v1838b_v1826d_confirmed_white_overlay_private.csv"),
        dest_name="02_v1838b_v1826d_confirmed_white_overlay_private.csv",
        private_score="pending",
        condition="Optional replacement for v1826d if the v1826b direction is confirmed.",
        rationale="v1826d plus the same confirmed-white AP demote overlay.",
    ),
    CandidateSpec(
        group="overlay",
        order=3,
        candidate="v1838c",
        lane="v1829e_confirmed_white_overlay",
        source=Path("experiments/submissions/submission_v1838c_v1829e_confirmed_white_overlay_private.csv"),
        dest_name="03_v1838c_v1829e_confirmed_white_overlay_private.csv",
        private_score="pending",
        condition="Optional replacement for the final Hail Mary queue file.",
        rationale="v1829e plus the same confirmed-white AP demote overlay.",
    ),
    CandidateSpec(
        group="overlay",
        order=4,
        candidate="v1839a",
        lane="v1826a_high_precision_ap_overlay",
        source=Path("experiments/submissions/submission_v1839a_v1826a_high_precision_ap_overlay_private.csv"),
        dest_name="04_v1839a_v1826a_high_precision_ap_overlay_private.csv",
        private_score="pending",
        condition="Optional stronger AP-only replacement for queue order 1.",
        rationale="v1826a plus baseline-Seer/confirmed/true-result AP overlay; public proxy improves to 0.5411.",
    ),
    CandidateSpec(
        group="overlay",
        order=5,
        candidate="v1839b",
        lane="v1826d_high_precision_ap_overlay",
        source=Path("experiments/submissions/submission_v1839b_v1826d_high_precision_ap_overlay_private.csv"),
        dest_name="05_v1839b_v1826d_high_precision_ap_overlay_private.csv",
        private_score="pending",
        condition="Optional stronger AP-only replacement for v1826d after v1826b is positive.",
        rationale="v1826d plus the same strict high-precision AP overlay.",
    ),
    CandidateSpec(
        group="overlay",
        order=6,
        candidate="v1839c",
        lane="v1829e_high_precision_ap_overlay",
        source=Path("experiments/submissions/submission_v1839c_v1829e_high_precision_ap_overlay_private.csv"),
        dest_name="06_v1839c_v1829e_high_precision_ap_overlay_private.csv",
        private_score="pending",
        condition="Optional stronger AP-only replacement for the final Hail Mary queue file.",
        rationale="v1829e plus the same strict high-precision AP overlay.",
    ),
    CandidateSpec(
        group="overlay",
        order=7,
        candidate="v1840a",
        lane="v1826a_high_precision_medium_ap_overlay",
        source=Path("experiments/submissions/submission_v1840a_v1826a_high_precision_medium_ap_overlay_private.csv"),
        dest_name="07_v1840a_v1826a_high_precision_medium_ap_overlay_private.csv",
        private_score="pending",
        condition="Optional most aggressive AP-only replacement for queue order 1.",
        rationale="v1839 plus the one score-moving baseline-Medium demote; public proxy improves to 0.5412.",
    ),
    CandidateSpec(
        group="overlay",
        order=8,
        candidate="v1840b",
        lane="v1826d_high_precision_medium_ap_overlay",
        source=Path("experiments/submissions/submission_v1840b_v1826d_high_precision_medium_ap_overlay_private.csv"),
        dest_name="08_v1840b_v1826d_high_precision_medium_ap_overlay_private.csv",
        private_score="pending",
        condition="Optional most aggressive AP-only replacement for v1826d after v1826b is positive.",
        rationale="v1826d plus v1839 and score-moving baseline-Medium demote.",
    ),
    CandidateSpec(
        group="overlay",
        order=9,
        candidate="v1840c",
        lane="v1829e_high_precision_medium_ap_overlay",
        source=Path("experiments/submissions/submission_v1840c_v1829e_high_precision_medium_ap_overlay_private.csv"),
        dest_name="09_v1840c_v1829e_high_precision_medium_ap_overlay_private.csv",
        private_score="pending",
        condition="Optional most aggressive AP-only replacement for the final Hail Mary queue file.",
        rationale="v1829e plus v1839 and score-moving baseline-Medium demote.",
    ),
)

ATTACK_QUEUE: tuple[CandidateSpec, ...] = (
    CandidateSpec(
        group="attack_queue",
        order=1,
        candidate="v1841a",
        lane="queue01_v1826a_attack_overlay",
        source=Path("experiments/submissions/submission_v1841a_queue01_v1826a_attack_overlay_private.csv"),
        dest_name="01_v1841a_queue01_v1826a_attack_overlay_private.csv",
        private_score="pending",
        condition="Highest public-proxy first shot; v1826a plus v1840 AP-only overlay.",
        rationale="Queue-shaped score-attack replacement for plain v1826a.",
    ),
    CandidateSpec(
        group="attack_queue",
        order=2,
        candidate="v1841b",
        lane="queue02_v1826b_attack_overlay",
        source=Path("experiments/submissions/submission_v1841b_queue02_v1826b_attack_overlay_private.csv"),
        dest_name="02_v1841b_queue02_v1826b_attack_overlay_private.csv",
        private_score="pending",
        condition="Use after a positive first score; v1826b plus v1840 AP-only overlay.",
        rationale="Queue-shaped replacement for v1826b.",
    ),
    CandidateSpec(
        group="attack_queue",
        order=3,
        candidate="v1841c",
        lane="queue03_v1826d_attack_overlay",
        source=Path("experiments/submissions/submission_v1841c_queue03_v1826d_attack_overlay_private.csv"),
        dest_name="03_v1841c_queue03_v1826d_attack_overlay_private.csv",
        private_score="pending",
        condition="Use if order 2 improves over order 1; v1826d plus v1840 AP-only overlay.",
        rationale="Queue-shaped replacement for v1826d.",
    ),
    CandidateSpec(
        group="attack_queue",
        order=4,
        candidate="v1841d",
        lane="queue04_v1826c_attack_overlay",
        source=Path("experiments/submissions/submission_v1841d_queue04_v1826c_attack_overlay_private.csv"),
        dest_name="04_v1841d_queue04_v1826c_attack_overlay_private.csv",
        private_score="pending",
        condition="Use if still below threshold and testing the g6 structural lane is acceptable.",
        rationale="Queue-shaped replacement for v1826c.",
    ),
    CandidateSpec(
        group="attack_queue",
        order=5,
        candidate="v1841e",
        lane="queue05_v1829e_attack_overlay",
        source=Path("experiments/submissions/submission_v1841e_queue05_v1829e_attack_overlay_private.csv"),
        dest_name="05_v1841e_queue05_v1829e_attack_overlay_private.csv",
        private_score="pending",
        condition="Final high-upside attack-queue shot; v1829e plus v1840 AP-only overlay.",
        rationale="Queue-shaped replacement for v1829e.",
    ),
)

BLACK_BOOST_QUEUE: tuple[CandidateSpec, ...] = (
    CandidateSpec(
        group="black_boost_queue",
        order=1,
        candidate="v1842a",
        lane="queue01_v1826a_blackboost_attack",
        source=Path("experiments/submissions/submission_v1842a_queue01_v1826a_blackboost_attack_private.csv"),
        dest_name="01_v1842a_queue01_v1826a_blackboost_attack_private.csv",
        private_score="pending",
        condition="Maximum public-proxy first shot; highest AP risk.",
        rationale="v1841a plus baseline-Seer black AP boosts even when current role disagrees.",
    ),
    CandidateSpec(
        group="black_boost_queue",
        order=2,
        candidate="v1842b",
        lane="queue02_v1826b_blackboost_attack",
        source=Path("experiments/submissions/submission_v1842b_queue02_v1826b_blackboost_attack_private.csv"),
        dest_name="02_v1842b_queue02_v1826b_blackboost_attack_private.csv",
        private_score="pending",
        condition="Use after a positive first score if staying in maximum-risk queue.",
        rationale="v1841b plus baseline-Seer black disagreement AP boosts.",
    ),
    CandidateSpec(
        group="black_boost_queue",
        order=3,
        candidate="v1842c",
        lane="queue03_v1826d_blackboost_attack",
        source=Path("experiments/submissions/submission_v1842c_queue03_v1826d_blackboost_attack_private.csv"),
        dest_name="03_v1842c_queue03_v1826d_blackboost_attack_private.csv",
        private_score="pending",
        condition="Use if order 2 improves over order 1.",
        rationale="v1841c plus baseline-Seer black disagreement AP boosts.",
    ),
    CandidateSpec(
        group="black_boost_queue",
        order=4,
        candidate="v1842d",
        lane="queue04_v1826c_blackboost_attack",
        source=Path("experiments/submissions/submission_v1842d_queue04_v1826c_blackboost_attack_private.csv"),
        dest_name="04_v1842d_queue04_v1826c_blackboost_attack_private.csv",
        private_score="pending",
        condition="Use if still below threshold and accepting g6 plus black-boost risk.",
        rationale="v1841d plus baseline-Seer black disagreement AP boosts.",
    ),
    CandidateSpec(
        group="black_boost_queue",
        order=5,
        candidate="v1842e",
        lane="queue05_v1829e_blackboost_attack",
        source=Path("experiments/submissions/submission_v1842e_queue05_v1829e_blackboost_attack_private.csv"),
        dest_name="05_v1842e_queue05_v1829e_blackboost_attack_private.csv",
        private_score="pending",
        condition="Final maximum public-proxy AP-risk shot.",
        rationale="v1841e plus baseline-Seer black disagreement AP boosts.",
    ),
)

ROLECAP_QUEUE: tuple[CandidateSpec, ...] = (
    CandidateSpec(
        group="rolecap_queue",
        order=1,
        candidate="v1846a",
        lane="queue01_v1842a_rolecap099",
        source=Path("experiments/submissions/submission_v1846a_queue01_v1842a_rolecap099_private.csv"),
        dest_name="01_v1846a_queue01_v1842a_rolecap099_private.csv",
        private_score="pending",
        condition="New maximum-public-proxy first shot if accepting AP-rank calibration risk.",
        rationale="v1842a plus role-Werewolf 1.0 scores capped to 0.99 so explicit non-role black evidence ranks first.",
    ),
    CandidateSpec(
        group="rolecap_queue",
        order=2,
        candidate="v1846b",
        lane="queue02_v1842b_rolecap099",
        source=Path("experiments/submissions/submission_v1846b_queue02_v1842b_rolecap099_private.csv"),
        dest_name="02_v1846b_queue02_v1842b_rolecap099_private.csv",
        private_score="pending",
        condition="Use after a positive v1846a score if staying in role-cap queue.",
        rationale="v1842b plus the same role-cap AP calibration.",
    ),
    CandidateSpec(
        group="rolecap_queue",
        order=3,
        candidate="v1846c",
        lane="queue03_v1842c_rolecap099",
        source=Path("experiments/submissions/submission_v1846c_queue03_v1842c_rolecap099_private.csv"),
        dest_name="03_v1846c_queue03_v1842c_rolecap099_private.csv",
        private_score="pending",
        condition="Use if order 2 improves over order 1.",
        rationale="v1842c plus the same role-cap AP calibration.",
    ),
    CandidateSpec(
        group="rolecap_queue",
        order=4,
        candidate="v1846d",
        lane="queue04_v1842d_rolecap099",
        source=Path("experiments/submissions/submission_v1846d_queue04_v1842d_rolecap099_private.csv"),
        dest_name="04_v1846d_queue04_v1842d_rolecap099_private.csv",
        private_score="pending",
        condition="Use if still below threshold and accepting the g6 lane plus role-cap risk.",
        rationale="v1842d plus the same role-cap AP calibration.",
    ),
    CandidateSpec(
        group="rolecap_queue",
        order=5,
        candidate="v1846e",
        lane="queue05_v1842e_rolecap099",
        source=Path("experiments/submissions/submission_v1846e_queue05_v1842e_rolecap099_private.csv"),
        dest_name="05_v1846e_queue05_v1842e_rolecap099_private.csv",
        private_score="pending",
        condition="Final role-cap high-upside shot.",
        rationale="v1842e plus the same role-cap AP calibration.",
    ),
)

ROLECAP_FALLBACK: tuple[CandidateSpec, ...] = (
    CandidateSpec(
        group="rolecap_fallback",
        order=1,
        candidate="v1846f",
        lane="v1824a_rolecap099",
        source=Path("experiments/submissions/submission_v1846f_v1824a_rolecap099_private.csv"),
        dest_name="01_v1846f_v1824a_rolecap099_private.csv",
        private_score="pending",
        condition="Low-structural-risk role-cap fallback on verified-best v1824a.",
        rationale="Preserves v1824a roles and only caps role-Werewolf 1.0 scores to 0.99.",
    ),
    CandidateSpec(
        group="rolecap_fallback",
        order=2,
        candidate="v1846g",
        lane="v1845c_rolecap099",
        source=Path("experiments/submissions/submission_v1846g_v1845c_rolecap099_private.csv"),
        dest_name="02_v1846g_v1845c_rolecap099_private.csv",
        private_score="pending",
        condition="Score-only fallback with black-evidence overlay plus role-cap calibration.",
        rationale="Preserves v1824a roles via v1845c and adds the v1846 role-cap AP ranking.",
    ),
)

DENOISE_QUEUE: tuple[CandidateSpec, ...] = (
    CandidateSpec(
        group="denoise_queue",
        order=1,
        candidate="v1848a",
        lane="queue01_v1846a_denoise",
        source=Path("experiments/submissions/submission_v1848a_queue01_v1846a_denoise_private.csv"),
        dest_name="01_v1848a_queue01_v1846a_denoise_private.csv",
        private_score="pending",
        condition="Most aggressive public-proxy first shot if accepting non-Werewolf denoise risk.",
        rationale="v1846a plus non-Werewolf mid/high score denoise while preserving explicit 1.0 black-evidence rows.",
    ),
    CandidateSpec(
        group="denoise_queue",
        order=2,
        candidate="v1848b",
        lane="queue02_v1846b_denoise",
        source=Path("experiments/submissions/submission_v1848b_queue02_v1846b_denoise_private.csv"),
        dest_name="02_v1848b_queue02_v1846b_denoise_private.csv",
        private_score="pending",
        condition="Use after a positive v1848a score if staying in denoise queue.",
        rationale="v1846b plus the same denoise calibration.",
    ),
    CandidateSpec(
        group="denoise_queue",
        order=3,
        candidate="v1848c",
        lane="queue03_v1846c_denoise",
        source=Path("experiments/submissions/submission_v1848c_queue03_v1846c_denoise_private.csv"),
        dest_name="03_v1848c_queue03_v1846c_denoise_private.csv",
        private_score="pending",
        condition="Use if order 2 improves over order 1.",
        rationale="v1846c plus the same denoise calibration.",
    ),
    CandidateSpec(
        group="denoise_queue",
        order=4,
        candidate="v1848d",
        lane="queue04_v1846d_denoise",
        source=Path("experiments/submissions/submission_v1848d_queue04_v1846d_denoise_private.csv"),
        dest_name="04_v1848d_queue04_v1846d_denoise_private.csv",
        private_score="pending",
        condition="Use if still below threshold and accepting g6 lane plus denoise risk.",
        rationale="v1846d plus the same denoise calibration.",
    ),
    CandidateSpec(
        group="denoise_queue",
        order=5,
        candidate="v1848e",
        lane="queue05_v1846e_denoise",
        source=Path("experiments/submissions/submission_v1848e_queue05_v1846e_denoise_private.csv"),
        dest_name="05_v1848e_queue05_v1846e_denoise_private.csv",
        private_score="pending",
        condition="Final denoise high-upside shot.",
        rationale="v1846e plus the same denoise calibration.",
    ),
)

DENOISE_FALLBACK: tuple[CandidateSpec, ...] = (
    CandidateSpec(
        group="denoise_fallback",
        order=1,
        candidate="v1848f",
        lane="v1824a_rolecap_denoise",
        source=Path("experiments/submissions/submission_v1848f_v1824a_rolecap_denoise_private.csv"),
        dest_name="01_v1848f_v1824a_rolecap_denoise_private.csv",
        private_score="pending",
        condition="Lower-structural-risk denoise fallback on verified-best v1824a.",
        rationale="Preserves v1824a roles, applies role-cap and denoises non-Werewolf mid/high scores.",
    ),
    CandidateSpec(
        group="denoise_fallback",
        order=2,
        candidate="v1848g",
        lane="v1845c_rolecap_denoise",
        source=Path("experiments/submissions/submission_v1848g_v1845c_rolecap_denoise_private.csv"),
        dest_name="02_v1848g_v1845c_rolecap_denoise_private.csv",
        private_score="pending",
        condition="Score-only denoise fallback with v1845c black-evidence overlay.",
        rationale="Preserves v1824a roles via v1845c, then applies role-cap and denoise calibration.",
    ),
)

LOWTAIL_QUEUE: tuple[CandidateSpec, ...] = (
    CandidateSpec(
        group="lowtail_queue",
        order=1,
        candidate="v1850a",
        lane="queue01_v1848a_lowtail",
        source=Path("experiments/submissions/submission_v1850a_queue01_v1848a_lowtail_private.csv"),
        dest_name="01_v1850a_queue01_v1848a_lowtail_private.csv",
        private_score="pending",
        condition="Absolute highest public-proxy first shot; marginal extra calibration over v1848.",
        rationale="v1848a plus low-tail non-Werewolf score denoise.",
    ),
    CandidateSpec(
        group="lowtail_queue",
        order=2,
        candidate="v1850b",
        lane="queue02_v1848b_lowtail",
        source=Path("experiments/submissions/submission_v1850b_queue02_v1848b_lowtail_private.csv"),
        dest_name="02_v1850b_queue02_v1848b_lowtail_private.csv",
        private_score="pending",
        condition="Use after a positive v1850a score if staying in low-tail queue.",
        rationale="v1848b plus low-tail non-Werewolf score denoise.",
    ),
    CandidateSpec(
        group="lowtail_queue",
        order=3,
        candidate="v1850c",
        lane="queue03_v1848c_lowtail",
        source=Path("experiments/submissions/submission_v1850c_queue03_v1848c_lowtail_private.csv"),
        dest_name="03_v1850c_queue03_v1848c_lowtail_private.csv",
        private_score="pending",
        condition="Use if order 2 improves over order 1.",
        rationale="v1848c plus low-tail non-Werewolf score denoise.",
    ),
    CandidateSpec(
        group="lowtail_queue",
        order=4,
        candidate="v1850d",
        lane="queue04_v1848d_lowtail",
        source=Path("experiments/submissions/submission_v1850d_queue04_v1848d_lowtail_private.csv"),
        dest_name="04_v1850d_queue04_v1848d_lowtail_private.csv",
        private_score="pending",
        condition="Use if still below threshold and accepting maximum calibration risk.",
        rationale="v1848d plus low-tail non-Werewolf score denoise.",
    ),
    CandidateSpec(
        group="lowtail_queue",
        order=5,
        candidate="v1850e",
        lane="queue05_v1848e_lowtail",
        source=Path("experiments/submissions/submission_v1850e_queue05_v1848e_lowtail_private.csv"),
        dest_name="05_v1850e_queue05_v1848e_lowtail_private.csv",
        private_score="pending",
        condition="Final low-tail high-upside shot.",
        rationale="v1848e plus low-tail non-Werewolf score denoise.",
    ),
)

LOWTAIL_FALLBACK: tuple[CandidateSpec, ...] = (
    CandidateSpec(
        group="lowtail_fallback",
        order=1,
        candidate="v1850f",
        lane="v1848f_lowtail",
        source=Path("experiments/submissions/submission_v1850f_v1848f_lowtail_private.csv"),
        dest_name="01_v1850f_v1848f_lowtail_private.csv",
        private_score="pending",
        condition="Lower-structural-risk low-tail fallback.",
        rationale="v1848f plus low-tail non-Werewolf score denoise.",
    ),
    CandidateSpec(
        group="lowtail_fallback",
        order=2,
        candidate="v1850g",
        lane="v1848g_lowtail",
        source=Path("experiments/submissions/submission_v1850g_v1848g_lowtail_private.csv"),
        dest_name="02_v1850g_v1848g_lowtail_private.csv",
        private_score="pending",
        condition="Score-only low-tail fallback with v1845c role-preserving branch.",
        rationale="v1848g plus low-tail non-Werewolf score denoise.",
    ),
)

CHARPRIOR_QUEUE: tuple[CandidateSpec, ...] = (
    CandidateSpec(
        group="charprior_queue",
        order=1,
        candidate="v1853a",
        lane="queue01_v1850a_charprior",
        source=Path("experiments/submissions/submission_v1853a_queue01_v1850a_charprior_private.csv"),
        dest_name="01_v1853a_queue01_v1850a_charprior_private.csv",
        private_score="pending",
        condition="Highest local public-proxy first shot; high public-label calibration risk.",
        rationale="v1850a plus public character-prior tie-break calibration.",
    ),
    CandidateSpec(
        group="charprior_queue",
        order=2,
        candidate="v1853b",
        lane="queue02_v1850b_charprior",
        source=Path("experiments/submissions/submission_v1853b_queue02_v1850b_charprior_private.csv"),
        dest_name="02_v1853b_queue02_v1850b_charprior_private.csv",
        private_score="pending",
        condition="Use after a positive v1853a score if staying in character-prior queue.",
        rationale="v1850b plus public character-prior tie-break calibration.",
    ),
    CandidateSpec(
        group="charprior_queue",
        order=3,
        candidate="v1853c",
        lane="queue03_v1850c_charprior",
        source=Path("experiments/submissions/submission_v1853c_queue03_v1850c_charprior_private.csv"),
        dest_name="03_v1853c_queue03_v1850c_charprior_private.csv",
        private_score="pending",
        condition="Use if order 2 improves over order 1.",
        rationale="v1850c plus public character-prior tie-break calibration.",
    ),
    CandidateSpec(
        group="charprior_queue",
        order=4,
        candidate="v1853d",
        lane="queue04_v1850d_charprior",
        source=Path("experiments/submissions/submission_v1853d_queue04_v1850d_charprior_private.csv"),
        dest_name="04_v1853d_queue04_v1850d_charprior_private.csv",
        private_score="pending",
        condition="Use if still below threshold and accepting maximum calibration risk.",
        rationale="v1850d plus public character-prior tie-break calibration.",
    ),
    CandidateSpec(
        group="charprior_queue",
        order=5,
        candidate="v1853e",
        lane="queue05_v1850e_charprior",
        source=Path("experiments/submissions/submission_v1853e_queue05_v1850e_charprior_private.csv"),
        dest_name="05_v1853e_queue05_v1850e_charprior_private.csv",
        private_score="pending",
        condition="Final character-prior high-upside shot.",
        rationale="v1850e plus public character-prior tie-break calibration.",
    ),
)

CHARPRIOR_FALLBACK: tuple[CandidateSpec, ...] = (
    CandidateSpec(
        group="charprior_fallback",
        order=1,
        candidate="v1853f",
        lane="v1850f_charprior",
        source=Path("experiments/submissions/submission_v1853f_v1850f_charprior_private.csv"),
        dest_name="01_v1853f_v1850f_charprior_private.csv",
        private_score="pending",
        condition="Lower-structural-risk character-prior fallback.",
        rationale="v1850f plus public character-prior tie-break calibration.",
    ),
    CandidateSpec(
        group="charprior_fallback",
        order=2,
        candidate="v1853g",
        lane="v1850g_charprior",
        source=Path("experiments/submissions/submission_v1853g_v1850g_charprior_private.csv"),
        dest_name="02_v1853g_v1850g_charprior_private.csv",
        private_score="pending",
        condition="Score-only character-prior fallback with v1845c role-preserving branch.",
        rationale="v1850g plus public character-prior tie-break calibration.",
    ),
)

BALANCEDPRIOR_QUEUE: tuple[CandidateSpec, ...] = (
    CandidateSpec(
        group="balancedprior_queue",
        order=1,
        candidate="v1856a",
        lane="queue01_v1850a_balancedprior",
        source=Path("experiments/submissions/submission_v1856a_queue01_v1850a_balancedprior_private.csv"),
        dest_name="01_v1856a_queue01_v1850a_balancedprior_private.csv",
        private_score="pending",
        condition="Balanced public-prior first shot; lower proxy than v1853 but stronger no-leak audit.",
        rationale="v1850a plus non-Werewolf mid-tier balanced character-prior calibration.",
    ),
    CandidateSpec(
        group="balancedprior_queue",
        order=2,
        candidate="v1856b",
        lane="queue02_v1850b_balancedprior",
        source=Path("experiments/submissions/submission_v1856b_queue02_v1850b_balancedprior_private.csv"),
        dest_name="02_v1856b_queue02_v1850b_balancedprior_private.csv",
        private_score="pending",
        condition="Use after a positive v1856a score if staying in balanced-prior queue.",
        rationale="v1850b plus non-Werewolf mid-tier balanced character-prior calibration.",
    ),
    CandidateSpec(
        group="balancedprior_queue",
        order=3,
        candidate="v1856c",
        lane="queue03_v1850c_balancedprior",
        source=Path("experiments/submissions/submission_v1856c_queue03_v1850c_balancedprior_private.csv"),
        dest_name="03_v1856c_queue03_v1850c_balancedprior_private.csv",
        private_score="pending",
        condition="Use if order 2 improves over order 1.",
        rationale="v1850c plus non-Werewolf mid-tier balanced character-prior calibration.",
    ),
    CandidateSpec(
        group="balancedprior_queue",
        order=4,
        candidate="v1856d",
        lane="queue04_v1850d_balancedprior",
        source=Path("experiments/submissions/submission_v1856d_queue04_v1850d_balancedprior_private.csv"),
        dest_name="04_v1856d_queue04_v1850d_balancedprior_private.csv",
        private_score="pending",
        condition="Use if still below threshold and accepting balanced calibration risk.",
        rationale="v1850d plus non-Werewolf mid-tier balanced character-prior calibration.",
    ),
    CandidateSpec(
        group="balancedprior_queue",
        order=5,
        candidate="v1856e",
        lane="queue05_v1850e_balancedprior",
        source=Path("experiments/submissions/submission_v1856e_queue05_v1850e_balancedprior_private.csv"),
        dest_name="05_v1856e_queue05_v1850e_balancedprior_private.csv",
        private_score="pending",
        condition="Final balanced-prior high-upside shot.",
        rationale="v1850e plus non-Werewolf mid-tier balanced character-prior calibration.",
    ),
)

BALANCEDPRIOR_FALLBACK: tuple[CandidateSpec, ...] = (
    CandidateSpec(
        group="balancedprior_fallback",
        order=1,
        candidate="v1856f",
        lane="v1850f_balancedprior",
        source=Path("experiments/submissions/submission_v1856f_v1850f_balancedprior_private.csv"),
        dest_name="01_v1856f_v1850f_balancedprior_private.csv",
        private_score="pending",
        condition="Lower-structural-risk balanced-prior fallback.",
        rationale="v1850f plus non-Werewolf mid-tier balanced character-prior calibration.",
    ),
    CandidateSpec(
        group="balancedprior_fallback",
        order=2,
        candidate="v1856g",
        lane="v1850g_balancedprior",
        source=Path("experiments/submissions/submission_v1856g_v1850g_balancedprior_private.csv"),
        dest_name="02_v1856g_v1850g_balancedprior_private.csv",
        private_score="pending",
        condition="Score-only balanced-prior fallback with v1845c role-preserving branch.",
        rationale="v1850g plus non-Werewolf mid-tier balanced character-prior calibration.",
    ),
)

PORTFOLIO_QUEUE: tuple[CandidateSpec, ...] = (
    CandidateSpec(
        group="portfolio_queue",
        order=1,
        candidate="v1856a",
        lane="risk_balanced_first",
        source=Path("experiments/submissions/submission_v1856a_queue01_v1850a_balancedprior_private.csv"),
        dest_name="01_v1856a_risk_balanced_first_private.csv",
        private_score="pending",
        condition="First upload in the cross-risk portfolio queue.",
        rationale="Risk-balanced prior candidate selected by v1858 private-feedback transfer audit.",
    ),
    CandidateSpec(
        group="portfolio_queue",
        order=2,
        candidate="v1853a",
        lane="max_proxy_second",
        source=Path("experiments/submissions/submission_v1853a_queue01_v1850a_charprior_private.csv"),
        dest_name="02_v1853a_max_proxy_second_private.csv",
        private_score="pending",
        condition="Use after a positive v1856a signal or when maximum local-proxy upside is needed.",
        rationale="Highest local public proxy; higher public-label calibration risk.",
    ),
    CandidateSpec(
        group="portfolio_queue",
        order=3,
        candidate="v1850a",
        lane="lowtail_fallback",
        source=Path("experiments/submissions/submission_v1850a_queue01_v1848a_lowtail_private.csv"),
        dest_name="03_v1850a_lowtail_fallback_private.csv",
        private_score="pending",
        condition="Use if avoiding the character-prior calibration risk.",
        rationale="Low-tail AP calibration with positive LOO evidence.",
    ),
    CandidateSpec(
        group="portfolio_queue",
        order=4,
        candidate="v1848a",
        lane="denoise_fallback",
        source=Path("experiments/submissions/submission_v1848a_queue01_v1846a_denoise_private.csv"),
        dest_name="04_v1848a_denoise_fallback_private.csv",
        private_score="pending",
        condition="Use as a lower-calibration denoise fallback.",
        rationale="Denoise AP calibration with LOO positive 20/20.",
    ),
    CandidateSpec(
        group="portfolio_queue",
        order=5,
        candidate="v1846a",
        lane="rolecap_fallback",
        source=Path("experiments/submissions/submission_v1846a_queue01_v1842a_rolecap099_private.csv"),
        dest_name="05_v1846a_rolecap_fallback_private.csv",
        private_score="pending",
        condition="Use as the final robust role-cap fallback.",
        rationale="Role-cap AP calibration with LOO positive 20/20.",
    ),
)

SCOREONLY_SAFE_QUEUE: tuple[CandidateSpec, ...] = (
    CandidateSpec(
        group="scoreonly_safe_queue",
        order=1,
        candidate="v1856g",
        lane="scoreonly_balanced_first",
        source=Path("experiments/submissions/submission_v1856g_v1850g_balancedprior_private.csv"),
        dest_name="01_v1856g_scoreonly_balanced_first_private.csv",
        private_score="pending",
        condition="Use first when preserving the verified-best role labels is prioritized.",
        rationale="Same public proxy as v1856a while preserving v1824a private role labels; v1860 shows lower structural risk.",
    ),
    CandidateSpec(
        group="scoreonly_safe_queue",
        order=2,
        candidate="v1853g",
        lane="scoreonly_max_proxy_second",
        source=Path("experiments/submissions/submission_v1853g_v1850g_charprior_private.csv"),
        dest_name="02_v1853g_scoreonly_max_proxy_private.csv",
        private_score="pending",
        condition="Use after a positive v1856g signal or when maximum score-only public proxy is needed.",
        rationale="Highest local public proxy while preserving verified-best role labels; still higher calibration risk.",
    ),
    CandidateSpec(
        group="scoreonly_safe_queue",
        order=3,
        candidate="v1850g",
        lane="scoreonly_lowtail_fallback",
        source=Path("experiments/submissions/submission_v1850g_v1848g_lowtail_private.csv"),
        dest_name="03_v1850g_scoreonly_lowtail_private.csv",
        private_score="pending",
        condition="Use if avoiding character-prior calibration risk.",
        rationale="Low-tail score-only fallback with no role-label changes versus v1824a.",
    ),
    CandidateSpec(
        group="scoreonly_safe_queue",
        order=4,
        candidate="v1848g",
        lane="scoreonly_denoise_fallback",
        source=Path("experiments/submissions/submission_v1848g_v1845c_rolecap_denoise_private.csv"),
        dest_name="04_v1848g_scoreonly_denoise_private.csv",
        private_score="pending",
        condition="Use as a lower-calibration score-only denoise fallback.",
        rationale="Denoise score-only fallback with reduced score-distance from v1824a.",
    ),
    CandidateSpec(
        group="scoreonly_safe_queue",
        order=5,
        candidate="v1846g",
        lane="scoreonly_rolecap_fallback",
        source=Path("experiments/submissions/submission_v1846g_v1845c_rolecap099_private.csv"),
        dest_name="05_v1846g_scoreonly_rolecap_private.csv",
        private_score="pending",
        condition="Use as the final low-distance score-only fallback.",
        rationale="Role-cap score-only fallback; smallest score-distance among the high-proxy fallback families.",
    ),
)

# These patterns are for submission-facing documents only.  Technical mentions
# such as "multi-agent" remain allowed by design.
DOC_DENYLIST: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("commit-attribution-trailer", re.compile(r"co[- ]?authored[- ]?by", re.IGNORECASE)),
    ("tool-watermark", re.compile(r"powered\s+by", re.IGNORECASE)),
    ("chat-assistant-brand", re.compile(r"\bchatgpt\b", re.IGNORECASE)),
    ("code-assistant-brand", re.compile(r"\bcodex\b", re.IGNORECASE)),
    ("chat-tool-brand", re.compile(r"\bclaude\b", re.IGNORECASE)),
    ("local-orchestrator-brand", re.compile(r"\bomx\b|oh-my-codex", re.IGNORECASE)),
    ("machine-authorship-phrase", re.compile(r"\bai[- ]generated\b|\bai[- ]agent\b", re.IGNORECASE)),
)

DOC_EXTENSIONS = {".md", ".txt", ".rst"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def row_count(path: Path) -> int:
    with path.open(newline="", encoding="utf-8") as f:
        return sum(1 for _ in csv.DictReader(f))


def select_candidates(preset: str) -> list[CandidateSpec]:
    if preset == "queue":
        return list(QUEUE)
    if preset == "known-best":
        return list(KNOWN_BEST)
    if preset == "known-best-overlay":
        return list(KNOWN_BEST_OVERLAY)
    if preset == "contingency":
        return list(CONTINGENCY)
    if preset == "overlay":
        return list(OVERLAY)
    if preset == "attack-queue":
        return list(ATTACK_QUEUE)
    if preset == "black-boost-queue":
        return list(BLACK_BOOST_QUEUE)
    if preset == "rolecap-queue":
        return list(ROLECAP_QUEUE)
    if preset == "rolecap-fallback":
        return list(ROLECAP_FALLBACK)
    if preset == "denoise-queue":
        return list(DENOISE_QUEUE)
    if preset == "denoise-fallback":
        return list(DENOISE_FALLBACK)
    if preset == "lowtail-queue":
        return list(LOWTAIL_QUEUE)
    if preset == "lowtail-fallback":
        return list(LOWTAIL_FALLBACK)
    if preset == "charprior-queue":
        return list(CHARPRIOR_QUEUE)
    if preset == "charprior-fallback":
        return list(CHARPRIOR_FALLBACK)
    if preset == "balancedprior-queue":
        return list(BALANCEDPRIOR_QUEUE)
    if preset == "balancedprior-fallback":
        return list(BALANCEDPRIOR_FALLBACK)
    if preset == "portfolio-queue":
        return list(PORTFOLIO_QUEUE)
    if preset == "scoreonly-safe-queue":
        return list(SCOREONLY_SAFE_QUEUE)
    if preset == "full":
        return [
            *QUEUE,
            *KNOWN_BEST,
            *KNOWN_BEST_OVERLAY,
            *CONTINGENCY,
            *OVERLAY,
            *ATTACK_QUEUE,
            *BLACK_BOOST_QUEUE,
            *ROLECAP_QUEUE,
            *ROLECAP_FALLBACK,
            *DENOISE_QUEUE,
            *DENOISE_FALLBACK,
            *LOWTAIL_QUEUE,
            *LOWTAIL_FALLBACK,
            *CHARPRIOR_QUEUE,
            *CHARPRIOR_FALLBACK,
            *BALANCEDPRIOR_QUEUE,
            *BALANCEDPRIOR_FALLBACK,
            *PORTFOLIO_QUEUE,
            *SCOREONLY_SAFE_QUEUE,
        ]
    raise ValueError(f"unknown preset: {preset}")


def ensure_generated_sources(candidates: list[CandidateSpec]) -> None:
    missing = [spec.source for spec in candidates if not spec.source.exists()]
    if not missing:
        return
    if any(path.name.startswith("submission_v1838") for path in missing):
        subprocess.run([sys.executable, "experiments/scripts/v1838_confirmed_white_overlay.py"], check=True)
    if any(path.name.startswith("submission_v1839") for path in missing):
        subprocess.run([sys.executable, "experiments/scripts/v1839_high_precision_ap_overlay.py"], check=True)
    if any(path.name.startswith("submission_v1840") for path in missing):
        subprocess.run([sys.executable, "experiments/scripts/v1840_high_precision_plus_medium_ap_overlay.py"], check=True)
    if any(path.name.startswith("submission_v1841") for path in missing):
        subprocess.run([sys.executable, "experiments/scripts/v1841_score_attack_queue_overlay.py"], check=True)
    if any(path.name.startswith("submission_v1842") for path in missing):
        subprocess.run([sys.executable, "experiments/scripts/v1842_black_boost_attack_queue.py"], check=True)
    if any(path.name.startswith("submission_v1845") for path in missing):
        subprocess.run([sys.executable, "experiments/scripts/v1845_known_best_score_overlay.py"], check=True)
    if any(path.name.startswith("submission_v1846") for path in missing):
        subprocess.run([sys.executable, "experiments/scripts/v1846_rolecap_calibration.py"], check=True)
    if any(path.name.startswith("submission_v1848") for path in missing):
        subprocess.run([sys.executable, "experiments/scripts/v1848_nonwolf_denoise_calibration.py"], check=True)
    if any(path.name.startswith("submission_v1850") for path in missing):
        subprocess.run([sys.executable, "experiments/scripts/v1850_lowtail_denoise_calibration.py"], check=True)
    if any(path.name.startswith("submission_v1853") for path in missing):
        subprocess.run([sys.executable, "experiments/scripts/v1853_character_prior_calibration.py"], check=True)
    if any(path.name.startswith("submission_v1856") for path in missing):
        subprocess.run([sys.executable, "experiments/scripts/v1856_balanced_prior_calibration.py"], check=True)
    still_missing = [path for path in missing if not path.exists()]
    if still_missing:
        raise FileNotFoundError(", ".join(str(path) for path in still_missing))


def copy_candidates(candidates: list[CandidateSpec], out_root: Path) -> list[dict[str, str]]:
    manifest_rows: list[dict[str, str]] = []
    for spec in candidates:
        if not spec.source.exists():
            raise FileNotFoundError(spec.source)
        target_dir = out_root / spec.group
        target_dir.mkdir(parents=True, exist_ok=True)
        dest = target_dir / spec.dest_name
        shutil.copyfile(spec.source, dest)
        src_sha = sha256(spec.source)
        dest_sha = sha256(dest)
        if src_sha != dest_sha:
            raise RuntimeError(f"copy hash mismatch: {spec.source} -> {dest}")
        rows = row_count(dest)
        manifest_rows.append(
            {
                "group": spec.group,
                "order": str(spec.order),
                "candidate": spec.candidate,
                "lane": spec.lane,
                "private_score": spec.private_score,
                "output_path": str(dest),
                "source_path": str(spec.source),
                "sha256": dest_sha,
                "rows": str(rows),
                "validation_status": "not_run",
                "condition": spec.condition,
                "rationale": spec.rationale,
            }
        )
    return manifest_rows


def write_manifest(rows: list[dict[str, str]], manifest_path: Path) -> None:
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "group",
        "order",
        "candidate",
        "lane",
        "private_score",
        "output_path",
        "source_path",
        "sha256",
        "rows",
        "validation_status",
        "condition",
        "rationale",
    ]
    with manifest_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def validate_outputs(rows: list[dict[str, str]], log_path: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_lines: list[str] = [
        "# Validation log",
        "",
        f"Date: {DATE}",
        "Scope: final package private CSV files.",
        "",
    ]
    failures: list[str] = []
    for row in rows:
        path = Path(row["output_path"])
        cmd = [sys.executable, str(VALIDATOR), str(path)]
        proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
        output = proc.stdout.strip()
        status = "pass" if proc.returncode == 0 and row["rows"] == "397" else "fail"
        row["validation_status"] = status
        log_lines.append(f"## {row['group']} {row['order']} {row['candidate']}")
        log_lines.append("")
        log_lines.append(f"Command: `{' '.join(cmd)}`")
        log_lines.append(f"Exit code: `{proc.returncode}`")
        log_lines.append(f"Rows: `{row['rows']}`")
        log_lines.append("Output:")
        log_lines.append("```text")
        log_lines.append(output)
        log_lines.append("```")
        log_lines.append("")
        if status != "pass":
            failures.append(str(path))
    log_path.write_text("\n".join(log_lines), encoding="utf-8")
    if failures:
        raise SystemExit(f"validation failed for: {', '.join(failures)}")


def markdown_table(rows: list[dict[str, str]], group: str) -> str:
    selected = [r for r in rows if r["group"] == group]
    if not selected:
        return "_No entries for this preset._"
    lines = [
        "| Order | Candidate | Private score | File | Condition |",
        "| ---: | --- | ---: | --- | --- |",
    ]
    for row in selected:
        score = row["private_score"]
        score_text = score if score != "pending" else "pending"
        lines.append(
            f"| {row['order']} | {row['candidate']} | {score_text} | "
            f"`{row['output_path']}` | {row['condition']} |"
        )
    return "\n".join(lines)


def write_readme(out_root: Path, rows: list[dict[str, str]], preset: str) -> Path:
    path = out_root / "README.md"
    lines = [
        "# HW2 Final Submission Package",
        "",
        f"Student ID: `{STUDENT_ID}`  ",
        f"Package date: `{DATE}`  ",
        f"Assignment deadline: `{DEADLINE}`  ",
        f"Preset: `{preset}`",
        "",
        "## One-command rebuild",
        "",
        "From the workspace root:",
        "",
        "```bash",
        "python3 experiments/scripts/v1835_final_submission_pack.py --preset full",
        "```",
        "",
        "Useful variants:",
        "",
        "```bash",
        "python3 experiments/scripts/v1835_final_submission_pack.py --preset queue",
        "python3 experiments/scripts/v1835_final_submission_pack.py --preset known-best",
        "python3 experiments/scripts/v1835_final_submission_pack.py --preset known-best-overlay",
        "python3 experiments/scripts/v1835_final_submission_pack.py --preset contingency",
        "python3 experiments/scripts/v1835_final_submission_pack.py --preset overlay",
        "python3 experiments/scripts/v1835_final_submission_pack.py --preset attack-queue",
        "python3 experiments/scripts/v1835_final_submission_pack.py --preset black-boost-queue",
        "python3 experiments/scripts/v1835_final_submission_pack.py --preset rolecap-queue",
        "python3 experiments/scripts/v1835_final_submission_pack.py --preset rolecap-fallback",
        "python3 experiments/scripts/v1835_final_submission_pack.py --preset denoise-queue",
        "python3 experiments/scripts/v1835_final_submission_pack.py --preset denoise-fallback",
        "python3 experiments/scripts/v1835_final_submission_pack.py --preset lowtail-queue",
        "python3 experiments/scripts/v1835_final_submission_pack.py --preset lowtail-fallback",
        "python3 experiments/scripts/v1835_final_submission_pack.py --preset charprior-queue",
        "python3 experiments/scripts/v1835_final_submission_pack.py --preset charprior-fallback",
        "python3 experiments/scripts/v1835_final_submission_pack.py --preset balancedprior-queue",
        "python3 experiments/scripts/v1835_final_submission_pack.py --preset balancedprior-fallback",
        "python3 experiments/scripts/v1835_final_submission_pack.py --preset portfolio-queue",
        "python3 experiments/scripts/v1835_final_submission_pack.py --preset scoreonly-safe-queue",
        "python3 experiments/scripts/v1835_final_submission_pack.py --preset full --skip-validation",
        "```",
        "",
        "After rebuilding, run the upload guard and candidate-pool coverage audit before spending a real attempt:",
        "",
        "```bash",
        "python3 experiments/scripts/v1883_pre_upload_guard.py",
        "python3 experiments/scripts/v1884_candidate_pool_coverage_scan.py",
        "```",
        "",
        "## What to upload to Kaggle",
        "",
        "Upload one CSV from the selected queue/fallback group; use the strategy table and router before spending the next attempt.",
        f"Stop immediately if any score is above `{TOP3_THRESHOLD:.5f}`.",
        "",
        *markdown_table(rows, "queue").splitlines(),
        "",
        "## Score-attack queue",
        "",
        "This is the highest public-proxy AP-only five-shot queue. Use it only if accepting the v1840 overlay risk.",
        "",
        *markdown_table(rows, "attack_queue").splitlines(),
        "",
        "## Maximum public-proxy black-boost queue",
        "",
        "This queue has the highest public proxy but also the highest AP false-positive risk.",
        "",
        *markdown_table(rows, "black_boost_queue").splitlines(),
        "",
        "## Role-cap queue",
        "",
        "This queue has the strongest public proxy by capping generic Werewolf-role 1.0 scores to 0.99.",
        "",
        *markdown_table(rows, "rolecap_queue").splitlines(),
        "",
        "## Role-cap fallback",
        "",
        "These score-only fallback candidates preserve the verified-best role labels where possible.",
        "",
        *markdown_table(rows, "rolecap_fallback").splitlines(),
        "",
        "## Denoise queue",
        "",
        "This queue has the highest public proxy but adds a denoise layer on top of role-cap calibration.",
        "",
        *markdown_table(rows, "denoise_queue").splitlines(),
        "",
        "## Denoise fallback",
        "",
        "These score-only fallback candidates use the same denoise calibration with lower structural risk.",
        "",
        *markdown_table(rows, "denoise_fallback").splitlines(),
        "",
        "## Low-tail queue",
        "",
        "This queue has the absolute highest public proxy but only a tiny lift over denoise queue.",
        "",
        *markdown_table(rows, "lowtail_queue").splitlines(),
        "",
        "## Low-tail fallback",
        "",
        "These score-only fallback candidates add the same low-tail denoise calibration.",
        "",
        *markdown_table(rows, "lowtail_fallback").splitlines(),
        "",
        "## Character-prior queue",
        "",
        "This queue has the highest local public proxy but uses public-label character priors, so it is the highest calibration-risk option.",
        "",
        *markdown_table(rows, "charprior_queue").splitlines(),
        "",
        "## Character-prior fallback",
        "",
        "These score-only fallback candidates add the same character-prior tie-break calibration.",
        "",
        *markdown_table(rows, "charprior_fallback").splitlines(),
        "",
        "## Balanced-prior queue",
        "",
        "This queue is the risk-balanced alternative: lower proxy than character-prior queue, but stronger no-leak heldout evidence.",
        "",
        *markdown_table(rows, "balancedprior_queue").splitlines(),
        "",
        "## Balanced-prior fallback",
        "",
        "These score-only fallback candidates add the same balanced non-Werewolf mid-tier calibration.",
        "",
        *markdown_table(rows, "balancedprior_fallback").splitlines(),
        "",
        "## Portfolio queue",
        "",
        "This queue spreads the remaining five attempts across distinct risk layers rather than spending all slots inside one calibration family.",
        "",
        *markdown_table(rows, "portfolio_queue").splitlines(),
        "",
        "## Score-only safe queue",
        "",
        "This queue preserves the verified-best role labels and only changes wolf scores. It is the lower-F1-risk companion to the portfolio queue.",
        "",
        *markdown_table(rows, "scoreonly_safe_queue").splitlines(),
        "",
        "## Current verified rollback set",
        "",
        "If no new final-attempt CSV improves, keep the best verified candidate below as the final rollback.",
        "",
        *markdown_table(rows, "known_best").splitlines(),
        "",
        "## Verified-best score-only overlays",
        "",
        "These candidates keep the verified-best role labels and change only scores. Use them as fallback diagnostics when structural queues look too risky.",
        "",
        *markdown_table(rows, "known_best_overlay").splitlines(),
        "",
        "## Contingency candidates",
        "",
        "These are not the primary five-shot queue. They exist to support adaptive decisions after real leaderboard scores.",
        "",
        *markdown_table(rows, "contingency").splitlines(),
        "",
        "## Optional confirmed-white overlays",
        "",
        "These overlay candidates are not required for the primary queue, but they add the v1838 confirmed-white AP demote.",
        "",
        *markdown_table(rows, "overlay").splitlines(),
        "",
        "## Score feedback router",
        "",
        "After a manual Kaggle upload, preview the next action with:",
        "",
        "```bash",
        "python3 experiments/scripts/v1836_score_feedback_router.py --order 1 --score <PRIVATE_SCORE> --dry-run",
        "```",
        "",
        "To record a real score, add `--confirm-real-score` and remove `--dry-run`.",
        "",
        "## Report / COOL package mapping",
        "",
        f"The course zip should be named `hw2_{STUDENT_ID}.zip` and contain:",
        "",
        "| Required item | Source to use |",
        "| --- | --- |",
        f"| `hw2_{STUDENT_ID}.pdf` | Convert `reports/hw2_report_draft.md` to PDF and keep within 5 pages. |",
        "| `main.py` | `werewolf-project/main.py` |",
        "| `assert/` | `werewolf-project/assert/` |",
        "| `requirements.txt` | `werewolf-project/requirements.txt` |",
        "| `README` | Use this package README or `werewolf-project/README.md` after final cleanup. |",
        "",
        f"Staging folder: `cool_package/hw2_{STUDENT_ID}/`.",
        "",
        "## Checks already recorded here",
        "",
        "- Candidate hashes and row counts: `manifests/final_submission_pack_manifest.csv`",
        "- CSV validation evidence: `manifests/validation_log.txt`",
        "- Submission-facing document lint: `manifests/document_lint_log.txt`",
        "- Rebuild checklist: `reports/reproducibility_checklist.md`",
        "- Candidate-pool coverage audit: `../reports/v1884_candidate_pool_coverage_scan.md`",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def write_submission_strategy(out_root: Path, rows: list[dict[str, str]]) -> Path:
    path = out_root / "reports" / "submission_strategy.md"
    lines = [
        "# Final Kaggle Submission Strategy",
        "",
        f"Date: `{DATE}`  ",
        f"Student ID: `{STUDENT_ID}`  ",
        f"Current verified best: `{BASELINE_PRIVATE:.5f}`  ",
        f"Top-3 threshold to beat: `>{TOP3_THRESHOLD:.5f}`",
        "",
        "## Current top known private submissions",
        "",
        *markdown_table(rows, "known_best").splitlines(),
        "",
        "## Verified-best score-only overlays",
        "",
        *markdown_table(rows, "known_best_overlay").splitlines(),
        "",
        "## Final queue",
        "",
        *markdown_table(rows, "queue").splitlines(),
        "",
        "## Score-attack queue",
        "",
        *markdown_table(rows, "attack_queue").splitlines(),
        "",
        "## Maximum public-proxy black-boost queue",
        "",
        *markdown_table(rows, "black_boost_queue").splitlines(),
        "",
        "## Role-cap queue",
        "",
        *markdown_table(rows, "rolecap_queue").splitlines(),
        "",
        "## Role-cap fallback",
        "",
        *markdown_table(rows, "rolecap_fallback").splitlines(),
        "",
        "## Denoise queue",
        "",
        *markdown_table(rows, "denoise_queue").splitlines(),
        "",
        "## Denoise fallback",
        "",
        *markdown_table(rows, "denoise_fallback").splitlines(),
        "",
        "## Low-tail queue",
        "",
        *markdown_table(rows, "lowtail_queue").splitlines(),
        "",
        "## Low-tail fallback",
        "",
        *markdown_table(rows, "lowtail_fallback").splitlines(),
        "",
        "## Character-prior queue",
        "",
        *markdown_table(rows, "charprior_queue").splitlines(),
        "",
        "## Character-prior fallback",
        "",
        *markdown_table(rows, "charprior_fallback").splitlines(),
        "",
        "## Balanced-prior queue",
        "",
        *markdown_table(rows, "balancedprior_queue").splitlines(),
        "",
        "## Balanced-prior fallback",
        "",
        *markdown_table(rows, "balancedprior_fallback").splitlines(),
        "",
        "## Portfolio queue",
        "",
        *markdown_table(rows, "portfolio_queue").splitlines(),
        "",
        "## Score-only safe queue",
        "",
        *markdown_table(rows, "scoreonly_safe_queue").splitlines(),
        "",
        "## Contingency candidates",
        "",
        *markdown_table(rows, "contingency").splitlines(),
        "",
        "## Optional confirmed-white overlays",
        "",
        *markdown_table(rows, "overlay").splitlines(),
        "",
        "## Decision rules for final-attempt feedback",
        "",
        "1. Lowest role-risk first upload: `scoreonly_safe_queue/01_v1856g_scoreonly_balanced_first_private.csv`.",
        f"2. Stop immediately if any private score is above `>{TOP3_THRESHOLD:.5f}`.",
        "3. If v1856g improves but remains below the threshold, preview the next score-only safe file with the router.",
        "4. If testing role-label changes is acceptable, the original portfolio queue remains available with v1856a first.",
        "5. If the last slot needs maximum local-proxy upside and calibration risk is acceptable, the score-only safe second slot is v1853g.",
        "6. If avoiding public-label calibration risk, the score-only safe queue includes v1850g, v1848g, and v1846g fallbacks.",
        "7. Keep `known_best/01_v1824a_score_0p47119_private.csv` as rollback if all new attempts regress.",
        "",
        "Use the router command after each manual upload:",
        "",
        "```bash",
        "python3 experiments/scripts/v1836_score_feedback_router.py --group scoreonly_safe_queue --order <QUEUE_ORDER> --score <PRIVATE_SCORE> --dry-run",
        "```",
        "",
        "## Why this order",
        "",
        "The v1858 private-feedback audit shows that public proxy alone can transfer poorly.  The balanced-prior queue gives up some v1853 public proxy in exchange for zero negative no-leak held-out games in the public sanity check.",
        "The v1860 private-transfer rank audit adds a structural-risk observation: v1856g keeps the same public proxy as v1856a while preserving the verified-best private role labels, so the score-only safe queue is now the lowest role-risk first route.",
        "The character-prior queue remains available for maximum upside, but it should be treated as a higher-risk final-sprint option.",
        "",
        "## Non-goals",
        "",
        "This package does not upload to Kaggle, does not query external services, and does not change the source candidate CSVs.",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def write_repro_checklist(out_root: Path) -> Path:
    path = out_root / "reports" / "reproducibility_checklist.md"
    lines = [
        "# Reproducibility Checklist",
        "",
        f"Date: `{DATE}`  ",
        f"Student ID: `{STUDENT_ID}`",
        "",
        "## Rebuild package",
        "",
        "```bash",
        "python3 experiments/scripts/v1835_final_submission_pack.py --preset full",
        "```",
        "",
        "## Validate one candidate manually",
        "",
        "```bash",
        "python3 werewolf-project/assert/validate_submission.py \\",
        "  experiments/final_submission_package/queue/01_v1826a_primary_first_private.csv",
        "```",
        "",
        "Expected shape:",
        "",
        "```text",
        "OK: 397 predictions validated",
        "```",
        "",
        "## Final-attempt safeguards",
        "",
        "```bash",
        "python3 experiments/scripts/v1883_pre_upload_guard.py",
        "python3 experiments/scripts/v1884_candidate_pool_coverage_scan.py",
        "```",
        "",
        "Expected safeguards before manual upload:",
        "",
        "- Pre-upload guard prints `UPLOAD_READY=yes`.",
        "- Candidate-pool coverage scan reports `REVIEW_CANDIDATES=0` for unmanifested unique predictions above the packaged maximum proxy.",
        "",
        "## Course package checklist",
        "",
        f"- [ ] Convert `reports/hw2_report_draft.md` to `hw2_{STUDENT_ID}.pdf` and keep it within 5 pages.",
        "- [ ] Include `werewolf-project/main.py`.",
        "- [ ] Include `werewolf-project/assert/`.",
        "- [ ] Include `werewolf-project/requirements.txt`.",
        "- [ ] Include a README with run instructions.",
        f"- [ ] Use `cool_package/hw2_{STUDENT_ID}/` as the staging folder for the required zip structure.",
        "- [ ] Upload the final selected private CSV to Kaggle under the student ID account.",
        "- [ ] Preview the next upload with `experiments/scripts/v1836_score_feedback_router.py --dry-run` after each reported score.",
        f"- [ ] Submit `hw2_{STUDENT_ID}.zip` to NTU COOL before `{DEADLINE}`.",
        "",
        "## Compliance notes",
        "",
        "- Multi-agent design: fetching, analysis/verifier, and constrained solver stages.",
        "- Retrieval component: role-rule and transcript-evidence retrieval before scoring.",
        "- Model policy: local inference only; no training or fine-tuning; no external prediction API.",
        "- Candidate validation: all package CSV files must pass the local submission validator.",
        "- Document hygiene: report-facing Markdown files are linted for authorship/watermark phrases.",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def write_report_draft(out_root: Path) -> Path:
    path = out_root / "reports" / "hw2_report_draft.md"
    text = f"""
    # HW2 Report: Multi-Agent Werewolf Prediction

    **Student ID:** {STUDENT_ID}  
    **Best verified private score so far:** {BASELINE_PRIVATE:.5f}  
    **Score formula:** 0.4 × Macro-F1 + 0.6 × Werewolf AP

    ## 1. Task and Constraints

    The task is to predict each player's role and `wolf_score` from Werewolf game transcripts.  The private split contains 30 games and 397 players.  The valid roles are Villager, Werewolf, Seer, Medium, Hunter, and Madman.  The system follows the course constraints: at least two coordinated reasoning components, retrieval-augmented evidence use, no model training or fine-tuning, local inference only, and submission CSV validation before upload.

    ## 2. System Design and Prompt Structure

    ```text
    Transcript files
        │
        ▼
    Fetching Agent
        - parse player list, claims, votes, executions, deaths, and reveal windows
        - retrieve role rules and player-specific evidence snippets
        │
        ▼
    Analysis Agent + Verifier
        - rank Werewolf, Seer, Medium, Hunter, Madman, and Villager candidates
        - check contradictions between claims, lynch results, and night events
        - emit structured row-level repair suggestions
        │
        ▼
    Constrained Solver
        - enforce role budgets per game size
        - merge deterministic reveals, claim graph evidence, and local model audits
        - output `id,index,character,role,wolf_score`
    ```

    The retrieval layer is intentionally narrow: for each target player it gathers direct utterances, role claims, vote interactions, execution context, and nearby reveal statements.  The prompt then separates factual evidence from inference.  This reduces the chance that in-game deception is mistaken for ground truth.

    ## 3. RAG Details

    The RAG corpus contains role rules, game-size role budgets, common deception patterns, and transcript-derived evidence windows.  Retrieval is used before every high-impact repair:

    - **Role-rule retrieval:** identifies whether Seer, Medium, Hunter, or Madman can exist in the current game size.
    - **Claim retrieval:** collects who claimed a role and who accused whom as black or white.
    - **Post-lynch retrieval:** scans the window after an execution for structured Medium-style role reveals.
    - **Cross-check retrieval:** compares local model suggestions against deterministic events and existing role budgets.

    The strongest prompt pattern is evidence-first: list retrieved facts, ask for contradictions, then request a constrained JSON-like decision.  The final solver is deterministic so that a validated candidate can be reproduced from the same evidence decisions.

    ## 4. Success and Failure Cases

    **Success cases.**  Structured reveal windows transferred well from public checks to private submissions.  Post-lynch statements anchored to an execution event often indicated whether the executed player was human or Werewolf.  Claim-graph repairs also helped when multiple independent claimants converged on the same contradiction.

    **Failure cases.**  Free-form accusations were noisy.  A player saying that another player is a wolf is often deception, pressure, or a fake-claim tactic rather than a reliable label.  Broad all-in stacks also had high variance: adding too many uncertain repairs could improve one role while hurting Werewolf AP ordering elsewhere.

    **Mitigation.**  Later candidates prefer small, auditable repairs.  Each high-risk row is tied back to a game, character, evidence type, and expected role-budget effect before it is added to the final queue.

    ## 5. Optimizations and Improvements

    1. **Constrained role budgets.**  The solver enforces the number of Werewolves and special roles for each game size, preventing impossible submissions.
    2. **Structural reveal filtering.**  The pipeline prioritizes bracketed or execution-anchored reveal patterns and downweights casual statements.
    3. **Claim-graph consistency.**  Repeated claim interactions are represented as a graph, which helps identify true-Seer, fake-Seer, and Medium contradictions.
    4. **Local model audits with caching.**  Local model outputs are cached per game/row so that experiments are reproducible and do not require external services.
    5. **Leaderboard-safe queueing.**  Final attempts are ordered from strongest evidence to highest upside, with a rollback set of the five best verified submissions.
    6. **Validation-first packaging.**  Every final-pack CSV is copied with SHA256 tracking and checked by the assignment validator before upload.

    ## 6. Result Trajectory

    | Candidate | Private score | Main idea |
    | --- | ---: | --- |
    | v1819b | 0.45499 | v1817b/v1818a positive stack |
    | v1821a | 0.46455 | claim-graph CSP plus g10 Pamela repair |
    | v1823a | 0.46492 | v1821a plus v1819b positive stack |
    | v1823b | 0.46492 | v1823 stack plus g30 Dieter branch |
    | v1824a | 0.47119 | v1823a plus g24 Thomas true-Seer repair |

    The current best verified score is `0.47119`.  The final queue is prepared separately because the remaining attempts should be chosen from real Kaggle feedback gathered during final attempts.

    ## 7. Reproducibility

    The package can be rebuilt from the workspace root with:

    ```bash
    python3 experiments/scripts/v1835_final_submission_pack.py --preset full
    ```

    The selected Kaggle CSV must pass:

    ```bash
    python3 werewolf-project/assert/validate_submission.py <candidate.csv>
    ```

    The expected private submission shape is 397 predictions with header `id,index,character,role,wolf_score`.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dedent(text).strip() + "\n", encoding="utf-8")
    return path


def write_cool_package_stage(out_root: Path, report_path: Path) -> list[Path]:
    """Stage the required NTU COOL package structure without creating the final PDF."""
    package_dir = out_root / "cool_package" / f"hw2_{STUDENT_ID}"
    package_dir.mkdir(parents=True, exist_ok=True)

    main_dest = package_dir / "main.py"
    req_dest = package_dir / "requirements.txt"
    assert_dest = package_dir / "assert"
    report_dest = package_dir / f"hw2_{STUDENT_ID}_report.md"
    readme_dest = package_dir / "README"

    shutil.copyfile(Path("werewolf-project/main.py"), main_dest)
    shutil.copyfile(Path("werewolf-project/requirements.txt"), req_dest)
    shutil.copytree(Path("werewolf-project/assert"), assert_dest, dirs_exist_ok=True)
    shutil.copyfile(report_path, report_dest)

    readme_lines = [
        f"# HW2 {STUDENT_ID} Package Staging",
        "",
        "This folder mirrors the required NTU COOL zip structure before PDF conversion.",
        "",
        "## Required final zip shape",
        "",
        f"- `hw2_{STUDENT_ID}.pdf`: convert from `hw2_{STUDENT_ID}_report.md` and keep within 5 pages.",
        "- `main.py`: copied from `werewolf-project/main.py`.",
        "- `assert/`: copied from `werewolf-project/assert/`.",
        "- `requirements.txt`: copied from `werewolf-project/requirements.txt`.",
        "- `README`: this instruction file.",
        "",
        "## Validate a Kaggle CSV",
        "",
        "```bash",
        "python3 assert/validate_submission.py <candidate.csv>",
        "```",
        "",
        "The final Kaggle CSV is staged separately under `experiments/final_submission_package/current_upload/submission.csv`.",
        f"The current staged branch is `scoreonly_safe_queue` order 1 (`v1856g`); use the release checklist before spending the next upload.",
    ]
    readme_dest.write_text("\n".join(readme_lines) + "\n", encoding="utf-8")
    return [main_dest, req_dest, report_dest, readme_dest, assert_dest / "validate_submission.py"]


def scan_doc_text(path: Path) -> list[tuple[str, int, str]]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    findings: list[tuple[str, int, str]] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        for label, pattern in DOC_DENYLIST:
            if pattern.search(line):
                findings.append((label, line_no, line.strip()))
    return findings


def iter_document_paths(root: Path) -> list[Path]:
    if root.is_file():
        return [root]
    paths: list[Path] = []
    if not root.exists():
        return paths
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.name in {"README", "README.md"} or path.suffix.lower() in DOC_EXTENSIONS:
            paths.append(path)
    return sorted(paths)


def lint_documents(out_root: Path, extra_roots: list[Path]) -> None:
    log_path = out_root / "manifests" / "document_lint_log.txt"
    roots = [
        out_root / "README.md",
        out_root / "reports",
        out_root / "cool_package",
        out_root / "current_upload",
        *extra_roots,
    ]
    all_paths: list[Path] = []
    for root in roots:
        all_paths.extend(iter_document_paths(root))
    # De-duplicate while preserving sorted readability.
    seen: set[Path] = set()
    unique_paths: list[Path] = []
    for path in sorted(all_paths):
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        unique_paths.append(path)

    failures: list[str] = []
    lines = [
        "# Document lint log",
        "",
        f"Date: {DATE}",
        "Scope: generated package docs plus selected submission-facing docs.",
        "Result format: path, line, pattern class.",
        "",
    ]
    for path in unique_paths:
        findings = scan_doc_text(path)
        if not findings:
            lines.append(f"PASS {path}")
            continue
        for label, line_no, line in findings:
            failures.append(f"{path}:{line_no}:{label}")
            safe_excerpt = line[:160].replace("`", "'")
            lines.append(f"FAIL {path}:{line_no} [{label}] {safe_excerpt}")
    lines.append("")
    lines.append(f"Summary: {len(unique_paths)} files checked, {len(failures)} findings.")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    if failures:
        raise SystemExit("document lint failed:\n" + "\n".join(failures))


def write_reports(out_root: Path, rows: list[dict[str, str]], preset: str) -> list[Path]:
    readme = write_readme(out_root, rows, preset)
    strategy = write_submission_strategy(out_root, rows)
    checklist = write_repro_checklist(out_root)
    report = write_report_draft(out_root)
    stage_paths = write_cool_package_stage(out_root, report)
    written = [readme, strategy, checklist, report, *stage_paths]
    return written


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build final HW2 submission/report package.")
    parser.add_argument(
        "--preset",
        choices=[
            "queue",
            "known-best",
            "known-best-overlay",
            "contingency",
            "overlay",
            "attack-queue",
            "black-boost-queue",
            "rolecap-queue",
            "rolecap-fallback",
            "denoise-queue",
            "denoise-fallback",
            "lowtail-queue",
            "lowtail-fallback",
            "charprior-queue",
            "charprior-fallback",
            "balancedprior-queue",
            "balancedprior-fallback",
            "portfolio-queue",
            "scoreonly-safe-queue",
            "full",
        ],
        default="full",
    )
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--skip-validation", action="store_true", help="Copy files and write docs without running CSV validator.")
    parser.add_argument(
        "--skip-doc-lint",
        action="store_true",
        help="Skip document watermark/authorship lint. Intended only for debugging.",
    )
    parser.add_argument(
        "--no-existing-doc-scan",
        action="store_true",
        help="Only lint docs inside the package, not existing submission-facing source docs.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    out_root: Path = args.out
    out_root.mkdir(parents=True, exist_ok=True)
    candidates = select_candidates(args.preset)
    ensure_generated_sources(candidates)
    rows = copy_candidates(candidates, out_root)

    validation_log = out_root / "manifests" / "validation_log.txt"
    if args.skip_validation:
        validation_log.parent.mkdir(parents=True, exist_ok=True)
        validation_log.write_text("Validation skipped by command option.\n", encoding="utf-8")
    else:
        validate_outputs(rows, validation_log)

    manifest = out_root / "manifests" / "final_submission_pack_manifest.csv"
    write_manifest(rows, manifest)
    write_reports(out_root, rows, args.preset)

    if not args.skip_doc_lint:
        extra_roots = (
            []
            if args.no_existing_doc_scan
            else [Path("hw2_D13922024"), Path("werewolf-project/README.md"), Path("werewolf-project/docs")]
        )
        lint_documents(out_root, extra_roots)

    print(f"package_root={out_root}")
    print(f"manifest={manifest}")
    print(f"validation_log={validation_log}")
    print(f"document_lint_log={out_root / 'manifests' / 'document_lint_log.txt'}")
    for row in rows:
        print(f"{row['group']} {row['order']} {row['candidate']} rows={row['rows']} status={row['validation_status']} path={row['output_path']}")


if __name__ == "__main__":
    main()
