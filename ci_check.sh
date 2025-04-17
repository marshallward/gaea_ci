export CI_COMMIT_SHA=`git rev-parse HEAD`
export CI_PROJECT_DIR=.
export JOB_DIR=tmp2
export STATS_REPO_BRANCH=c5
export CONFIGS_REPO_BRANCH=c5_update

.gitlab/pipeline-ci-tool.sh check-stats pgi S
.gitlab/pipeline-ci-tool.sh check-stats pgi N
.gitlab/pipeline-ci-tool.sh check-stats pgi L
.gitlab/pipeline-ci-tool.sh check-params pgi

.gitlab/pipeline-ci-tool.sh check-stats intel S
.gitlab/pipeline-ci-tool.sh check-stats intel N
.gitlab/pipeline-ci-tool.sh check-stats intel L
.gitlab/pipeline-ci-tool.sh check-params intel

.gitlab/pipeline-ci-tool.sh check-stats gnu S
.gitlab/pipeline-ci-tool.sh check-stats gnu N
.gitlab/pipeline-ci-tool.sh check-stats gnu L
.gitlab/pipeline-ci-tool.sh check-stats gnu T
.gitlab/pipeline-ci-tool.sh check-stats gnu D
.gitlab/pipeline-ci-tool.sh check-params gnu
