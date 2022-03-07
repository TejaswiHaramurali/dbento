*** Settings ***
Library   SSHLibrary
Library   OperatingSystem
Library   Process

*** Variables ***
${SERVER_CMD}               python3.6 scripts/server.py --ipaddress 127.0.0.1 --port 5555 --partitions 6 --rate_limit 50
${CLIENT_CMD}               python3.6 scripts/reverse_engineering_client.py --ipaddress 127.0.0.1 --port 5555 --rate_limit 50

${SERVER_OUTPUT}       /tmp/ticrconsole.log
${CLIENT_OUTPUT}       /tmp/ticrlog.txt

*** Keywords ***

Check for installation of Pandas on client machine
        ${output}=    Run    pip3.6 show pandas
        Log    ${output}
        Should Contain    ${output}    Name: pandas


Start up server process
        ${server_handle}=    Start Process    ${SERVER_CMD}    shell=True    stdout=server-output.txt
        BuiltIn.Sleep    2s
        Process Should Be Running    ${server_handle}
        Set Global Variable    ${server_handle}


Start up client process
        ${client_handle}=    Start Process    ${CLIENT_CMD}    shell=True    stdout=client-output.txt
        Process Should Be Running    ${client_handle}
        Set Global Variable    ${client_handle}

        
Wait for client process
        ${result} =    Wait For Process    ${client_handle}    timeout=600 secs
        Process Should Be Stopped    ${client_handle}	
        Should Be Equal As Integers    ${result.rc}    0


End server process
        Send Signal To Process    SIGINT    ${server_handle}
        BuiltIn.Sleep    2s
        Process Should Be Stopped    ${server_handle}


Compare file contents
        ${server_output} =    Get File    server_symbols.txt
        ${client_output} =    Get File    client_symbols.txt
        BuiltIn.Log To Console    ${server_output}
        BuiltIn.Log To Console    ${client_output}
        Should Be Equal As Strings    ${server_output}    ${client_output}


*** Testcases ***

Verify installation of Pandas on client machine
        Check for installation of Pandas on client machine

Verify server startup
        Start up server process

Verify client startup
        Start up client process

Verify client ends cleanly
        Wait for client process

Terminate server process
        End server process

Compare final result
        Compare file contents
