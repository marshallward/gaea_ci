export CI_COMMIT_SHA=`git rev-parse HEAD`
export CI_PROJECT_DIR=.
export JOB_DIR=tmp2
export STATS_REPO_BRANCH=c5
export CONFIGS_REPO_BRANCH=c5_update

#.gitlab/pipeline-ci-tool.sh create-job-dir gnu SNLDT

#.gitlab/pipeline-ci-tool.sh copy-test-space gnu
#.gitlab/pipeline-ci-tool.sh run-suite gnu SNLDT
#.gitlab/pipeline-ci-tool.sh run-suite gnu R

.gitlab/pipeline-ci-tool.sh create-job-dir intel SNL
.gitlab/pipeline-ci-tool.sh copy-test-space intel
.gitlab/pipeline-ci-tool.sh run-suite intel SNL

#.gitlab/pipeline-ci-tool.sh copy-test-space pgi
#.gitlab/pipeline-ci-tool.sh run-suite pgi SNL
