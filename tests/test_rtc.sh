docker build . -t test
docker run -v $(pwd):/output --rm --user $(id -u):$(id -g) test --granule S1A_IW_GRDH_1SDV_20171209T043028_20171209T043053_019621_021551_C522 -l -i --username $username --password $pass
