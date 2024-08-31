:: 学号
set name=
:: 校园网密码（默认为身份证后 8 位）
set pwd=
:: 设备 ip
set ip=

:: GET 请求（该接口为校园网登录页 100.64.13.17 的官方接口）
curl "http://100.64.13.17:801/eportal/portal/login?callback=dr1003&login_method=1&user_account=%%2C0%%2C%name%&user_password=%pwd%&wlan_user_ip=%ip%&wlan_user_ipv6=&wlan_user_mac=000000000000&wlan_ac_ip=100.64.13.18&wlan_ac_name=&jsVersion=4.1.3&terminal_type=1&lang=zh-cn&v=5545&lang=zh"

:: 让窗口保持打开状态
pause