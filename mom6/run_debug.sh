export CI_COMMIT_SHA=`git rev-parse HEAD`
export CI_PROJECT_DIR=.
export JOB_DIR=tmp

#.gitlab/pipeline-ci-tool.sh create-job-dir gnu SNLDT
.gitlab/pipeline-ci-tool.sh copy-test-space gnu
.gitlab/pipeline-ci-tool.sh run-suite gnu SNLDT
