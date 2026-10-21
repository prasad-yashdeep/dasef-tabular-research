#!/usr/bin/env bash
# One-shot public release of the DASEF repository for the DMLR submission.
#   1. builds the supplementary zip (paper/dmlr/supplement/dasef_supplement.zip, < 100 MB)
#   2. packs the large artifacts that git does not track into release-asset tarballs
#   3. records the working tree on the current local branch (the full private history stays local)
#   4. builds a clean public snapshot of that commit (internal planning documents, reviewer notes,
#      superseded paper versions and backups excluded) on branch $PUBLIC_BRANCH
#   5. creates the public GitHub repository, pushes the snapshot as its main branch, tags it and
#      publishes a release with the tarballs and the supplementary zip attached
# Network steps ask for confirmation; set ASSUME_YES=1 for a non-interactive run, SKIP_PACK=1 to reuse an existing zip and tarballs.
# Run from the repo root with the virtualenv active:
#   bash scripts/release/prepare_release.sh            # full flow
#   bash scripts/release/prepare_release.sh --no-push  # steps 1 to 4 only (nothing leaves the machine)
set -euo pipefail
cd "$(dirname "$0")/../.."
REPO_SLUG="${REPO_SLUG:-prasad-yashdeep/dasef-tabular-research}"
TAG="${TAG:-v1.1-dmlr-submission}"
PUBLIC_BRANCH="${PUBLIC_BRANCH:-public-release}"
ASSETS="${ASSETS:-${TMPDIR:-/tmp}/dasef_release_assets}"   # outside the tree: never committed, never zipped
NO_PUSH=0; [ "${1:-}" = "--no-push" ] && NO_PUSH=1

# Paths kept out of the public snapshot (they remain in the private history): internal plans and runbooks,
# audits and reviewer notes, superseded paper versions and drafts, the submission checklist, dead scripts.
PUBLIC_EXCLUDE=(docs paper/dmlr/SUBMISSION_CHECKLIST.md paper/SANITY_AUDIT_2026-09-08.md scripts/loo_stability_analysis.py
  PAPER2_PLAN.md .learnings slides results/deepseek_judgment_shortlist results/sweep_summaries
  run_full_parallel.py run_schema_model.py run_paper2_schemas.py scripts/gepa_experiment.py scripts/gepa_downstream_poc.py
  scripts/expansion/launch_expansion_gpt55.sh results/statistics/ANALYSIS_COMPLETE.md results/statistics/gemini31
  'results/statistics/clean_formula_controls_*' 'results/statistics/prospective_formula_controls_*'
  'results/statistics/downstream_awareness_*' 'results/statistics/existing_result_stats_*'
  results/postcutoff_real/run_plan.json results/postcutoff_real/run_plan.md cache/schemas/bngtic_tac_toe cache/schemas/bngbreast_w
  results/statistics/classical_baselines_onehot scripts/run_deepseek_judgment_shortlist.sh)

confirm() {
  if [ "${ASSUME_YES:-0}" = 1 ]; then echo "$1 [auto-yes]"; return 0; fi
  read -r -p "$1 [y/N] " ok; [ "$ok" = y ]
}

if [ "${SKIP_PACK:-0}" = 1 ] && [ -s paper/dmlr/supplement/dasef_supplement.zip ] && ls "$ASSETS"/*.tar.gz >/dev/null 2>&1; then
  echo "== 1/5 and 2/5 skipped (SKIP_PACK=1): reusing the zip and the tarballs in $ASSETS"
else
echo "== 1/5 supplementary zip"
python scripts/release/build_supplement.py

echo "== 2/5 release-asset tarballs (large artifacts not tracked by git)"
mkdir -p "$ASSETS"
pack() {  # pack <name> <find-root> <find-args...>
  local name=$1; shift; local root=$1; shift
  local list; list=$(mktemp)
  find "$root" "$@" -print > "$list"
  if [ -s "$list" ]; then
    tar -czf "$ASSETS/$name.tar.gz" -T "$list"
    echo "   $name.tar.gz: $(wc -l < "$list" | tr -d ' ') files, $(du -h "$ASSETS/$name.tar.gz" | cut -f1)"
  fi
  rm -f "$list"
}
pack matrices_core_judgments results/judgments -path '*/matrices/*.parquet'
pack judgment_rows_core results/judgments -path '*/judgments/*.json'
pack matrices_expansion results/expansion_offline -name '*.parquet'
pack matrices_postcutoff results/postcutoff_real -name '*.parquet'
pack matrices_prospective results/full_suite_prospective -name '*.parquet'
pack matrices_anonymized results/anonymized_control -name '*.parquet'
pack matrices_schema_runs results/schema_runs \( -name '*.parquet' -o -path '*/judgments/*.json' \)
pack local_cache_postcutoff_salmonella data/local_cache -path '*postcutoff_salmonella_serovar_*' -type f
ls -la "$ASSETS"
fi

echo "== 3/5 local commit on $(git branch --show-current)"
git add -A
echo "   files staged: $(git status --short | wc -l | tr -d ' ')"
git commit -q -m "DMLR submission ($TAG): one-hot encoding correction, five-draw random-expression control, release layout

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" || echo "   nothing to commit"

echo "== 4/5 public snapshot on branch $PUBLIC_BRANCH"
TMP_INDEX=$(mktemp)
rm -f "$TMP_INDEX"
excluded=("${PUBLIC_EXCLUDE[@]}")
while IFS= read -r p; do excluded+=("$p"); done < <(git ls-files paper | grep -v '^paper/dmlr/\|^paper/tables/' || true)
GIT_INDEX_FILE="$TMP_INDEX" git read-tree HEAD
GIT_INDEX_FILE="$TMP_INDEX" git rm -r -q --cached --ignore-unmatch -- "${excluded[@]}"
TREE=$(GIT_INDEX_FILE="$TMP_INDEX" git write-tree)
rm -f "$TMP_INDEX"
PARENT=()
if git fetch -q origin main 2>/dev/null && git rev-parse -q --verify origin/main >/dev/null; then PARENT=(-p origin/main); fi
SNAP=$(git commit-tree "$TREE" ${PARENT[@]+"${PARENT[@]}"} -m "DASEF public release $TAG

Code, cached schemas and raw generator responses, per-run scores, statistics, tables, figures and the DMLR paper source.
Stored feature matrices, judgment outputs and the prepared salmonella table are release assets of this tag.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>")
git branch -f "$PUBLIC_BRANCH" "$SNAP"
echo "   snapshot commit: $SNAP"
echo "   files: $(git ls-tree -r --name-only "$SNAP" | wc -l | tr -d ' ') | size: $(git ls-tree -r -l "$SNAP" | awk '{s+=$4} END {printf "%.1f MB", s/1e6}')"
LEAK_RE='^docs/\|SUBMISSION_CHECKLIST\|SANITY_AUDIT\|\.bak$\|^paper/[^/]*$\|^paper/p[0-9]\|^paper/page_\|loo_stability\|^PAPER2_PLAN\|^\.learnings\|^slides/\|deepseek_judgment_shortlist\|sweep_summaries\|^run_full_parallel\|^run_schema_model\|^run_paper2_schemas\|gepa_\|launch_expansion_gpt55\|ANALYSIS_COMPLETE\|^results/statistics/gemini31/\|^results/statistics/clean_formula_controls_\|^results/statistics/prospective_formula_controls_\|^results/statistics/downstream_awareness_\|^results/statistics/existing_result_stats_\|^results/postcutoff_real/run_plan\|bngtic_tac_toe\|bngbreast_w\|classical_baselines_onehot\|release_assets\|\.tar\.gz$'
leak=$(git ls-tree -r --name-only "$SNAP" | grep -c "$LEAK_RE" || true)
[ "$leak" = 0 ] || { echo "   ERROR: $leak excluded paths are still in the snapshot"; git ls-tree -r --name-only "$SNAP" | grep "$LEAK_RE" | head; exit 1; }
# machine-specific prefixes of the authors' workstation and harness scratch directories (split so this file does not match itself)
STRAY1='/Users/dece''ntral'; STRAY2='/private/tmp/cla''ude'; STRAY3='/tmp/cla''ude'
stray=$(git grep -I -l -e "$STRAY1" -e "$STRAY2" -e "$STRAY3" "$SNAP" -- . | sed "s/^$SNAP://" || true)
[ -z "$stray" ] || { echo "   ERROR: machine-specific paths inside the snapshot:"; echo "$stray" | head; exit 1; }
[ "$(git ls-tree -r --name-only "$SNAP" | grep -c 'data/local_cache/.*/data.parquet')" -ge 11 ] || { echo "   ERROR: cached tables missing from the snapshot"; exit 1; }

[ "$NO_PUSH" = 1 ] && { echo "== --no-push: stopping before any network action (inspect with: git ls-tree -r --name-only $PUBLIC_BRANCH)"; exit 0; }

echo "== 5/5 publish"
confirm "Create PUBLIC repository github.com/$REPO_SLUG and push branch $PUBLIC_BRANCH as its main branch?" || { echo "aborted"; exit 1; }
if ! git remote get-url origin >/dev/null 2>&1; then
  gh repo create "$REPO_SLUG" --public --source=. --remote=origin --description "DASEF: controlled benchmark for LLM tabular feature engineering (DMLR submission)"
fi
git push -u origin "$PUBLIC_BRANCH:main"
confirm "Publish release $TAG with the tarballs in $ASSETS and the supplementary zip?" || { echo "pushed code only; release skipped"; exit 0; }
git tag -f "$TAG" "$SNAP" && git push -f origin "$TAG"
gh release create "$TAG" "$ASSETS"/*.tar.gz paper/dmlr/supplement/dasef_supplement.zip --title "DMLR submission artifacts ($TAG)" \
  --notes "Stored feature matrices (Parquet), per-row judgment outputs, the prepared salmonella table (CC BY 4.0), and the supplementary zip submitted with the paper; everything else is in the repository. Matrices derived from the prediction-market and web-tracker tables carry their CC BY-NC 4.0 and CC BY-NC-SA 4.0 terms (see data/local_cache/NOTICE.md). See README.md for the reproduction commands and CHANGELOG.md for the corrections in this version."
echo "done: https://github.com/$REPO_SLUG (branch main = snapshot $SNAP, tag $TAG)"
