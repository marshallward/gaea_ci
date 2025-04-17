export CI_COMMIT_SHA=`git rev-parse HEAD`
export CI_PROJECT_DIR=.
export JOB_DIR=tmp3
export STATS_REPO_BRANCH=c5
#export CONFIGS_REPO_BRANCH=c5

.gitlab/pipeline-ci-tool.sh -x create-job-dir
.gitlab/pipeline-ci-tool.sh -x mrs-compile debug_gnu
.gitlab/pipeline-ci-tool.sh mrs-compile repro_gnu mrs-compile static_gnu
.gitlab/pipeline-ci-tool.sh mrs-compile repro_intel
.gitlab/pipeline-ci-tool.sh mrs-compile repro_pgi
.gitlab/pipeline-ci-tool.sh nolibs-ocean-only-compile gnu
.gitlab/pipeline-ci-tool.sh nolibs-ocean-ice-compile gnu
