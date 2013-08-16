#!/bin/sh

# comments:
# this file is run as cron job on 10.0.6.200
# delete any vhd file when its timestamp is 1 days ago

start=`date`
path="/var/run/sr-mount/c35dd077-801e-b40b-a266-5fe149a671a2";
active_date=`/bin/date -d "1 days ago" +"%Y-%m-%d" `;

flag=0;

get_flag() {
	# compare file timestamp and 7 days ago
	a=$1
	b=$2
	if [[ $((  $(echo $a | tr -d '-')   -  $(echo $b | tr -d '-')  )) -lt 0 ]] ; then 
		flag=1
	else
		flag=0
	fi
}


temp_date=''

#
# delete vm physical file, in case of the phantom file still there
for i in $path/*.vhd ; do
	temp_date=`/usr/bin/stat -c %y ${i} | /bin/awk '{printf $1}'`

	get_flag $temp_date $active_date

	if [ $flag -gt 0 ]; then
		echo "$flag"
		echo $temp_date
		echo $active_date
		/bin/rm "$i"
	fi
done

# delete work is done

# get path that contains the most recent xva files, get last sunday string first
pre_sun='';

get_pr_sunday()
{
        for i in $(seq 0 7); do
                temp_date=`/bin/date -d "${i} days ago" +"%Y-%m-%d" `;
                temp_weekday=`/bin/date -d "${i} days ago" +"%w" `;
                if [ $temp_weekday -eq 0 ]; then
                        #echo "$temp_date   $temp_weekday";
                        pre_sun=$temp_date;
                fi
        done
}


get_pr_sunday;

for file in /mnt/xenimages/$pre_sun/*.xva
do
    echo "$file"
    /usr/bin/xe vm-import filename=$file preserve=true # never background, put & here
    #delete resotred files, 
    #/bin/rm $file

    #/usr/bin/xe vm-import filename=$file preserve=true  &

    #NPROC=$(($NPROC+1))
    #if [ "$NPROC" -ge 2 ]; then
    #    wait
    #    echo "I am waiting"
    #    NPROC=0
    #fi

done

end=`date`
# send email
/bin/echo -e "start: "$start" \r\nend: "$end | /bin/mail -s "xen VM restore done" support@wutest.com -- -f no-reply@wutest.com

