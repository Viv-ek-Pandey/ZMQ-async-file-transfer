#!/bin/bash

init() {
    # USERS
    # List users
    sudo -u mattermost /opt/mattermost/bin/mmctl --local user list

    # Create users
    sudo -u mattermost /opt/mattermost/bin/mmctl --local user create --email yogesh@datamotive.io --username yogesh --password Datamotive@123 --firstname Yogesh --lastname Anyapanawar
    sudo -u mattermost /opt/mattermost/bin/mmctl --local user create --email sameerz@datamotive.io --username sameer --password Datamotive@123 --firstname Sameer --lastname Zaveri
    sudo -u mattermost /opt/mattermost/bin/mmctl --local user create --email sourav@datamotive.io --username sourav --password Datamotive@123 --firstname Sourav --lastname Patjoshi
    sudo -u mattermost /opt/mattermost/bin/mmctl --local user create --email rishabh@datamotive.io --username rishabh --password Datamotive@123 --firstname Rishabh --lastname Kemni
    sudo -u mattermost /opt/mattermost/bin/mmctl --local user create --email vaibhav@datamotive.io --username vaibhav --password Datamotive@123 --firstname Vaibhav --lastname Tekade
    sudo -u mattermost /opt/mattermost/bin/mmctl --local user create --email prateek@datamotive.io --username prateek --password Datamotive@123 --firstname Prateek --lastname Shetty
    sudo -u mattermost /opt/mattermost/bin/mmctl --local user create --email tushar@datamotive.io --username tushar --password Datamotive@123 --firstname Tushar --lastname Tarkas
    sudo -u mattermost /opt/mattermost/bin/mmctl --local user create --email vaibhavc@datamotive.io --username vaibhavc --password Datamotive@123 --firstname Vaibhav --lastname Chopade
    sudo -u mattermost /opt/mattermost/bin/mmctl --local user create --email akanksh@datamotive.io --username akanksh --password Datamotive@123 --firstname Akanksh --lastname Khochikar
    sudo -u mattermost /opt/mattermost/bin/mmctl --local user create --email amit@datamotive.io --username amit --password Datamotive@123 --firstname Amit --lastname Mane

    # TEAMS
    # List teams
    sudo -u mattermost /opt/mattermost/bin/mmctl --local team list

    # Create Teams
    sudo -u mattermost /opt/mattermost/bin/mmctl --local team create --name finance --display-name "Finance team"
    sudo -u mattermost /opt/mattermost/bin/mmctl --local team create --name hr --display-name "HR team"
    sudo -u mattermost /opt/mattermost/bin/mmctl --local team create --name marketing --display-name "Marketing team"
    sudo -u mattermost /opt/mattermost/bin/mmctl --local team create --name svann-all --display-name "Svann org"

    # Add users to teams
    # finance
    sudo -u mattermost /opt/mattermost/bin/mmctl --local team users add finance yogesh@datamotive.io yogesh
    sudo -u mattermost /opt/mattermost/bin/mmctl --local team users add finance user-5@sample.mattermost.com aaron.medina
    sudo -u mattermost /opt/mattermost/bin/mmctl --local team users add finance user-7@sample.mattermost.com aaron.peterson
    sudo -u mattermost /opt/mattermost/bin/mmctl --local team users add finance user-4@sample.mattermost.com anne.stone
    sudo -u mattermost /opt/mattermost/bin/mmctl --local team users add finance user-12@sample.mattermost.com ashley.berry

    # hr
    sudo -u mattermost /opt/mattermost/bin/mmctl --local team users add hr user-6@sample.mattermost.com christina.wilson
    sudo -u mattermost /opt/mattermost/bin/mmctl --local team users add hr user-11@sample.mattermost.com craig.reed
    sudo -u mattermost /opt/mattermost/bin/mmctl --local team users add hr user-8@sample.mattermost.com diana.wells
    sudo -u mattermost /opt/mattermost/bin/mmctl --local team users add hr user-14@sample.mattermost.com emily.meyer
    sudo -u mattermost /opt/mattermost/bin/mmctl --local team users add hr user-3@sample.mattermost.com jack.wheeler
    sudo -u mattermost /opt/mattermost/bin/mmctl --local team users add hr user-9@sample.mattermost.com karen.austin
    sudo -u mattermost /opt/mattermost/bin/mmctl --local team users add hr user-10@sample.mattermost.com robert.ward
    sudo -u mattermost /opt/mattermost/bin/mmctl --local team users add hr user-13@sample.mattermost.com samuel.palmer

    # marketing
    sudo -u mattermost /opt/mattermost/bin/mmctl --local team users add marketing sameerz@datamotive.io sameer
    sudo -u mattermost /opt/mattermost/bin/mmctl --local team users add marketing akanksh@datamotive.io akanksh
    sudo -u mattermost /opt/mattermost/bin/mmctl --local team users add marketing amit@datamotive.io amit
    sudo -u mattermost /opt/mattermost/bin/mmctl --local team users add marketing yogesh@datamotive.io yogesh
    sudo -u mattermost /opt/mattermost/bin/mmctl --local team users add marketing user-2@sample.mattermost.com samuel.tucker

    # engg
    sudo -u mattermost /opt/mattermost/bin/mmctl --local team users add engg tushar@datamotive.io tushar
    sudo -u mattermost /opt/mattermost/bin/mmctl --local team users add engg sourav@datamotive.io sourav
    sudo -u mattermost /opt/mattermost/bin/mmctl --local team users add engg rishabh@datamotive.io rishabh
    sudo -u mattermost /opt/mattermost/bin/mmctl --local team users add engg prateek@datamotive.io prateek
    sudo -u mattermost /opt/mattermost/bin/mmctl --local team users add engg vaibhav@datamotive.io vaibhav
    sudo -u mattermost /opt/mattermost/bin/mmctl --local team users add engg vaibhavc@datamotive.io vaibhavc

    # svann-all
    sudo -u mattermost /opt/mattermost/bin/mmctl --local team users add svann-all yogesh@datamotive.io yogesh
    sudo -u mattermost /opt/mattermost/bin/mmctl --local team users add svann-all user-5@sample.mattermost.com aaron.medina
    sudo -u mattermost /opt/mattermost/bin/mmctl --local team users add svann-all user-7@sample.mattermost.com aaron.peterson
    sudo -u mattermost /opt/mattermost/bin/mmctl --local team users add svann-all user-4@sample.mattermost.com anne.stone
    sudo -u mattermost /opt/mattermost/bin/mmctl --local team users add svann-all user-12@sample.mattermost.com ashley.berry
    sudo -u mattermost /opt/mattermost/bin/mmctl --local team users add svann-all user-6@sample.mattermost.com christina.wilson
    sudo -u mattermost /opt/mattermost/bin/mmctl --local team users add svann-all user-11@sample.mattermost.com craig.reed
    sudo -u mattermost /opt/mattermost/bin/mmctl --local team users add svann-all user-8@sample.mattermost.com diana.wells
    sudo -u mattermost /opt/mattermost/bin/mmctl --local team users add svann-all user-14@sample.mattermost.com emily.meyer
    sudo -u mattermost /opt/mattermost/bin/mmctl --local team users add svann-all user-3@sample.mattermost.com jack.wheeler
    sudo -u mattermost /opt/mattermost/bin/mmctl --local team users add svann-all user-9@sample.mattermost.com karen.austin
    sudo -u mattermost /opt/mattermost/bin/mmctl --local team users add svann-all user-10@sample.mattermost.com robert.ward
    sudo -u mattermost /opt/mattermost/bin/mmctl --local team users add svann-all user-13@sample.mattermost.com samuel.palmer
    sudo -u mattermost /opt/mattermost/bin/mmctl --local team users add svann-all sameerz@datamotive.io sameer
    sudo -u mattermost /opt/mattermost/bin/mmctl --local team users add svann-all akanksh@datamotive.io akanksh
    sudo -u mattermost /opt/mattermost/bin/mmctl --local team users add svann-all amit@datamotive.io amit
    sudo -u mattermost /opt/mattermost/bin/mmctl --local team users add svann-all yogesh@datamotive.io yogesh
    sudo -u mattermost /opt/mattermost/bin/mmctl --local team users add svann-all user-2@sample.mattermost.com samuel.tucker
    sudo -u mattermost /opt/mattermost/bin/mmctl --local team users add svann-all tushar@datamotive.io tushar
    sudo -u mattermost /opt/mattermost/bin/mmctl --local team users add svann-all sourav@datamotive.io sourav
    sudo -u mattermost /opt/mattermost/bin/mmctl --local team users add svann-all rishabh@datamotive.io rishabh
    sudo -u mattermost /opt/mattermost/bin/mmctl --local team users add svann-all prateek@datamotive.io prateek
    sudo -u mattermost /opt/mattermost/bin/mmctl --local team users add svann-all vaibhav@datamotive.io vaibhav
    sudo -u mattermost /opt/mattermost/bin/mmctl --local team users add svann-all vaibhavc@datamotive.io vaibhavc

    # CHANNELS
    # List channels
    sudo -u mattermost /opt/mattermost/bin/mmctl --local channel list hr

    # Create channels
    sudo -u mattermost /opt/mattermost/bin/mmctl --local channel create --team finance --name finance_channel --display-name "Channel for finance team"
    sudo -u mattermost /opt/mattermost/bin/mmctl --local channel create --team hr --name hr_channel --display-name "Channel for hr team"
    sudo -u mattermost /opt/mattermost/bin/mmctl --local channel create --team marketing --name marketing_channel --display-name "Channel for marketing team"
    sudo -u mattermost /opt/mattermost/bin/mmctl --local channel create --team engg --name engg_channel --display-name "Channel for engg team"
    sudo -u mattermost /opt/mattermost/bin/mmctl --local channel create --team svann-all --name svann-all_channel --display-name "Broadcast channel"

    # Add users to channels
    #finance
    sudo -u mattermost /opt/mattermost/bin/mmctl --local channel users add finance:finance_channel yogesh@datamotive.io yogesh
    sudo -u mattermost /opt/mattermost/bin/mmctl --local channel users add finance:finance_channel user-5@sample.mattermost.com aaron.medina
    sudo -u mattermost /opt/mattermost/bin/mmctl --local channel users add finance:finance_channel user-7@sample.mattermost.com aaron.peterson
    sudo -u mattermost /opt/mattermost/bin/mmctl --local channel users add finance:finance_channel user-4@sample.mattermost.com anne.stone
    sudo -u mattermost /opt/mattermost/bin/mmctl --local channel users add finance:finance_channel user-12@sample.mattermost.com ashley.berry

    #hr
    sudo -u mattermost /opt/mattermost/bin/mmctl --local channel users add hr:hr_channel user-6@sample.mattermost.com christina.wilson
    sudo -u mattermost /opt/mattermost/bin/mmctl --local channel users add hr:hr_channel user-11@sample.mattermost.com craig.reed
    sudo -u mattermost /opt/mattermost/bin/mmctl --local channel users add hr:hr_channel user-8@sample.mattermost.com diana.wells
    sudo -u mattermost /opt/mattermost/bin/mmctl --local channel users add hr:hr_channel user-14@sample.mattermost.com emily.meyer
    sudo -u mattermost /opt/mattermost/bin/mmctl --local channel users add hr:hr_channel user-3@sample.mattermost.com jack.wheeler
    sudo -u mattermost /opt/mattermost/bin/mmctl --local channel users add hr:hr_channel user-9@sample.mattermost.com karen.austin
    sudo -u mattermost /opt/mattermost/bin/mmctl --local channel users add hr:hr_channel user-10@sample.mattermost.com robert.ward
    sudo -u mattermost /opt/mattermost/bin/mmctl --local channel users add hr:hr_channel user-13@sample.mattermost.com samuel.palmer

    #marketing
    sudo -u mattermost /opt/mattermost/bin/mmctl --local channel users add marketing:marketing_channel sameerz@datamotive.io sameer
    sudo -u mattermost /opt/mattermost/bin/mmctl --local channel users add marketing:marketing_channel akanksh@datamotive.io akanksh
    sudo -u mattermost /opt/mattermost/bin/mmctl --local channel users add marketing:marketing_channel amit@datamotive.io amit
    sudo -u mattermost /opt/mattermost/bin/mmctl --local channel users add marketing:marketing_channel yogesh@datamotive.io yogesh
    sudo -u mattermost /opt/mattermost/bin/mmctl --local channel users add marketing:marketing_channel user-2@sample.mattermost.com samuel.tucker

    #engg
    sudo -u mattermost /opt/mattermost/bin/mmctl --local channel users add engg:engg_channel tushar@datamotive.io tushar
    sudo -u mattermost /opt/mattermost/bin/mmctl --local channel users add engg:engg_channel sourav@datamotive.io sourav
    sudo -u mattermost /opt/mattermost/bin/mmctl --local channel users add engg:engg_channel rishabh@datamotive.io rishabh
    sudo -u mattermost /opt/mattermost/bin/mmctl --local channel users add engg:engg_channel prateek@datamotive.io prateek
    sudo -u mattermost /opt/mattermost/bin/mmctl --local channel users add engg:engg_channel vaibhav@datamotive.io vaibhav
    sudo -u mattermost /opt/mattermost/bin/mmctl --local channel users add engg:engg_channel vaibhavc@datamotive.io vaibhavc

    #all
    sudo -u mattermost /opt/mattermost/bin/mmctl --local channel users add svann-all:svann-all_channel yogesh@datamotive.io yogesh
    sudo -u mattermost /opt/mattermost/bin/mmctl --local channel users add svann-all:svann-all_channel user-5@sample.mattermost.com aaron.medina
    sudo -u mattermost /opt/mattermost/bin/mmctl --local channel users add svann-all:svann-all_channel user-7@sample.mattermost.com aaron.peterson
    sudo -u mattermost /opt/mattermost/bin/mmctl --local channel users add svann-all:svann-all_channel user-4@sample.mattermost.com anne.stone
    sudo -u mattermost /opt/mattermost/bin/mmctl --local channel users add svann-all:svann-all_channel user-12@sample.mattermost.com ashley.berry
    sudo -u mattermost /opt/mattermost/bin/mmctl --local channel users add svann-all:svann-all_channel user-6@sample.mattermost.com christina.wilson
    sudo -u mattermost /opt/mattermost/bin/mmctl --local channel users add svann-all:svann-all_channel user-11@sample.mattermost.com craig.reed
    sudo -u mattermost /opt/mattermost/bin/mmctl --local channel users add svann-all:svann-all_channel user-8@sample.mattermost.com diana.wells
    sudo -u mattermost /opt/mattermost/bin/mmctl --local channel users add svann-all:svann-all_channel user-14@sample.mattermost.com emily.meyer
    sudo -u mattermost /opt/mattermost/bin/mmctl --local channel users add svann-all:svann-all_channel user-3@sample.mattermost.com jack.wheeler
    sudo -u mattermost /opt/mattermost/bin/mmctl --local channel users add svann-all:svann-all_channel user-9@sample.mattermost.com karen.austin
    sudo -u mattermost /opt/mattermost/bin/mmctl --local channel users add svann-all:svann-all_channel user-10@sample.mattermost.com robert.ward
    sudo -u mattermost /opt/mattermost/bin/mmctl --local channel users add svann-all:svann-all_channel user-13@sample.mattermost.com samuel.palmer
    sudo -u mattermost /opt/mattermost/bin/mmctl --local channel users add svann-all:svann-all_channel sameerz@datamotive.io sameer
    sudo -u mattermost /opt/mattermost/bin/mmctl --local channel users add svann-all:svann-all_channel akanksh@datamotive.io akanksh
    sudo -u mattermost /opt/mattermost/bin/mmctl --local channel users add svann-all:svann-all_channel amit@datamotive.io amit
    sudo -u mattermost /opt/mattermost/bin/mmctl --local channel users add svann-all:svann-all_channel yogesh@datamotive.io yogesh
    sudo -u mattermost /opt/mattermost/bin/mmctl --local channel users add svann-all:svann-all_channel user-2@sample.mattermost.com samuel.tucker
    sudo -u mattermost /opt/mattermost/bin/mmctl --local channel users add svann-all:svann-all_channel tushar@datamotive.io tushar
    sudo -u mattermost /opt/mattermost/bin/mmctl --local channel users add svann-all:svann-all_channel sourav@datamotive.io sourav
    sudo -u mattermost /opt/mattermost/bin/mmctl --local channel users add svann-all:svann-all_channel rishabh@datamotive.io rishabh
    sudo -u mattermost /opt/mattermost/bin/mmctl --local channel users add svann-all:svann-all_channel prateek@datamotive.io prateek
    sudo -u mattermost /opt/mattermost/bin/mmctl --local channel users add svann-all:svann-all_channel vaibhav@datamotive.io vaibhav
    sudo -u mattermost /opt/mattermost/bin/mmctl --local channel users add svann-all:svann-all_channel vaibhavc@datamotive.io vaibhavc
}

get_channels() 
{
    TOKEN=$1
    server=$2
    server_port=$3
    local channels=$(curl -H "Authorization: Bearer ${TOKEN}" http://${server}:${server_port}/api/v4/channels | jq -r '.[].id')
    echo $channels
}

post_messages_on_channel()
{
    TOKEN=$1
    server=$2
    server_port=$3
    channel_id=$4
    local cnt=$5
    #echo "Posting message on channel: ${channel}"
    # Get team id by name
    #team_id=$(curl -H "Authorization: Bearer ${TOKEN}" http://${server}:${server_port}/api/v4/teams/name/${team} | jq -r '.id')
    #echo "Fetched team id: ${team_id}"
    # Get channel id by name
    #channel_id=$(curl -H "Authorization: Bearer ${TOKEN}" http://${server}:${server_port}/api/v4/teams/${team_id}/channels/name/${channel} | jq -r '.id')
    #echo "Fetched channel id: ${channel_id}"

    # post messages using the channel id
    declare -a arr_msgs=(
        "Sync-up will be scheduled at 10:00 AM everyday." 
        "There will be a townhall meeting today at 4:00 PM" 
        "Release planning meeting got rescheduled"
        "When was the bug scrub done?"
        "Test infrastructure will be updated on Sunday at 08:00 PM. Hope all the backups are in place"
        "Infra team will renew licenses by end of this month"
        "Customer support team will publish the escalation data today. We will have to analyze it and identify top 3 impact zones of the product."
        "HR programs are published on internal-bulletin"
        "Salary credits may be delayed this month due to bank holidays"
        "New deals signed with Fusion Inc..."
        )
    echo "Posting ${cnt} Messages on Channel: "$channel_id
    while [ $cnt -gt 0 ] 
    do
        #echo "Message# ${count}"
        r=$(( $RANDOM % 10 ))
        msg=${arr_msgs[$r]}
        post_message="{\"channel_id\": \"${channel_id}\", \"message\": \"${msg}\"}"
        post_resp=$(curl -si -H "Authorization: Bearer ${TOKEN}" --request POST -d "${post_message}" http://${server}:${server_port}/api/v4/posts)
        (( cnt-- ))
    done
}

post_messages() {
    # Login
    server=$1
    server_port=$2
    uname=$3
    pwd=$4
    msg_cnt=$5
    echo "Logging in to server: ${server}"
    login_resp=$(curl -si -H "Content-Type: application/json" --request POST -d '{ "login_id": "'${uname}'", "password": "'${pwd}'" }' http://${server}:${server_port}/api/v4/users/login)
    head=true
    while read -r line; do
       if $head; then
           if [[ $line = $'\r' ]]; then
               head=false
           else
               header="$header"$'\n'"$line"
           fi
       else
           body="$body"$'\n'"$line"
       fi
    done < <(echo "$login_resp")
    user_id=$(echo $body | jq -r '.id')
    while IFS=':' read key value; do
        # trim whitespace in "value"
        value=${value##+([[:space:]])}; value=${value%%+([[:space:]])}

        case "$key" in
            Token) TOKEN="$value"
                    ;;
            HTTP*) read PROTO STATUS MSG <<< "$key{$value:+:$value}"
                    ;;
        esac
    done < <(echo "$login_resp")
    TOKEN="$(echo -e "${TOKEN}" | tr -d '[:space:]')"
    echo "User ID: ${user_id}"
    echo "Login status: ${STATUS}"
    echo "Login token: ${TOKEN}"

    # Get channels
    arr=$(get_channels $TOKEN $server $server_port)
    eval "channels=( $arr )"
    echo "Fetched all channels in system: ${#channels[@]}"
    # Post messages for each team's channels
    for channel in "${channels[@]}"
    do
        # Post messages on channel
        post_messages_on_channel $TOKEN $server $server_port $channel $msg_cnt
    done

    # Logout
    echo "Logging out"
    logout_resp=$(curl -si -H "Authorization: Bearer ${TOKEN}" -H "content-type: application/json" --request POST -d '{}' http://${server}:${server_port}/api/v4/users/logout)
}

recursive_post_messages() 
{
    while true; 
    do
        post_messages $1 $2 $3 $4 $5
        echo "Sleeping for 5 secs"
        sleep 5
    done
}
help()
{
    echo -e "USAGE: "
    echo -e "./mattermost_load.sh -mode= -server=[SERVER HOSTNAME | IP ADDRESS] -server_port=[SERVER PORT] -server_uname=[SERVER USERNAME] -server_pwd=[SERVER PASSWORD] -messages=[Count of messages]\n"
    echo -e "-mode (Optional): init-to create users, teams & channels in mattermost before starting to generate load. \n 
    always-to keep posting messages in a recursive manner. Messages will be posted to all channels in system at a fixed rate of number of messages specified by messages parameter per 1 minute. \n
    Default none. \n"
    echo -e "-server: IP Address or Hostname of Mattermost Server"
    echo -e "-server_port (Optional): Port number of Mattermost Server. Default is 8065"
    echo -e "-server_uname: Username of Mattermost Server APIs/GUI user. The user should be service account user having rights to create users, teams, channels & post messages in any channel."
    echo -e "-server_pwd: Password of Mattermost Server APIs/GUI user."
    echo -e "-messages: Number of messages to be sent \n"
    echo -e "-help: Command help \n"
}

main()
{
    if [[ $# -lt 4 ]];
    then
        echo "Please enter valid arguments..."
        help
        return
    elif [[ $1 = "--help" ]];
    then
        help
        return
    fi
    
    # Process args
    IFS="="
    for arg in "$@"; do
        read -ra arr <<< "$arg"
        flag=${arr[0]}
        val=${arr[1]}
        case "${flag}" in
            -mode) mode=${val};;
            -server) server=${val};;
            -server_port) server_port=${val};;
            -server_uname) uname=${val};;
            -server_pwd) pwd=${val};;
            -messages) msg_cnt=${val};;
        esac
    done
    echo "Generating load with following options: "
    echo "Mode: $mode";
    echo "Server: $server";
    echo "Server Port: $server_port";
    echo "Server Username: $uname";
    echo "Server Pwd: $pwd";
    echo "Messages: $msg_cnt\n";
    
    # Valdiate inputs
    if [[ $server == "" || $uname == "" || $pwd == "" || $msg_cnt == "" || $msg_cnt == 0 ]];
    then
        echo "Invalid parameters... Parameters server, server_uname, server_pwd & messages can't be empty"
        help
    fi
    # Set default port
    if [[ $server_port == "" ]];
    then
        server_port=8065
    fi
    # Check if init is required
    if [[ $mode = "init" ]];
    then
        init_1 $server $server_port $uname $pwd
    elif [[ $mode = "always" ]];
    then
        recursive_post_messages $server $server_port $uname $pwd $msg_cnt
    fi
    #Create messages
    post_messages $server $server_port $uname $pwd $msg_cnt
}
main $@
