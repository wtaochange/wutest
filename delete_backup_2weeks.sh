#!/bin/sh

# delete xen backup 2 weeks ago

path="/xenimages";
pre_sun='';

get_pr_sunday()
{
	for i in $(seq 0 14); do
        	temp_date=`/bin/date -v-${i}d +"%Y-%m-%d" `;
        	temp_weekday=`/bin/date -v-${i}d +"%w" `;
		if [ $temp_weekday -eq 0 ]; then
        		#echo "$temp_date   $temp_weekday";
			pre_sun=$temp_date;
		fi
	done
}

get_pr_sunday;

echo "$pre_sun";

/bin/rm -rf $path/$pre_sun

