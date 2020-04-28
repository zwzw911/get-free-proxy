#get_free_proxy
get_free_proxy is a tool to get free proxy from website
### install
`pip install get-free-proxy`
### usage
get_free_proxy depends on [gen_browser_header](https://github.com/zwzw911/gen-browser-header).   

create gen_browser_header setting  

`import gen_browser_header.setting.Setting as gbh_setting`   
`import gen_browser_header.self.SelfEnum as gbh_self_enum`     
`cur_gbh_setting = gbh_setting.GbhSetting()`    
`cur_gbh_setting.proxy_ip = ['10.11.12.13:8080']`    
`cur_gbh_setting.browser_type = {gbh_self_enum.BrowserType.All}`        
`cur_gbh_setting.firefox_ver = {'min': 74, 'max': 75}`    
`cur_gbh_setting.chrome_type = {gbh_self_enum.ChromeType.Stable}`    
`cur_gbh_setting.chrome_max_release_year = 1`    
`cur_gbh_setting.os_type = {gbh_self_enum.OsType.Win64}`

create get_free_proxy setting    
 
`import get_free_proxy.self.SelfEnum as gfp_self_enum`    
`import get_free_proxy.setting.Setting as gfp_setting`    
`cur_gfp_setting = gfp_setting.GfpSetting()`    
`cur_gfp_setting.proxy_type = {gfp_self_enum.ProxyType.HIGH_ANON}`    
`cur_gfp_setting.protocol = {gfp_self_enum.ProtocolType.HTTP,
                            gfp_self_enum.ProtocolType.HTTPS}`    
`cur_gfp_setting.country = {gfp_self_enum.Country.All}`    
`cur_gfp_setting.storage_type = {gfp_self_enum.StorageType.All}`    
`cur_gfp_setting.mysql = {
     'host': '127.0.0.1',
     'port': 3306,
     'user': 'root',
     'pwd': '1234',
     'db_name': 'db_proxy',
     'tbl_name': 'tbl_proxy',
     'charset': 'utf8mb4'}`    
`cur_gfp_setting.redis = {
    'host': '127.0.0.1',
    'port': 6379,
    'db': 0,  # 0~15
    'pwd': None
}`    
`cur_gfp_setting.result_file_path = os.path.join(tempfile.gettempdir(), 'result.json')`    
`cur_gfp_setting.valid_time_in_db = 86400`    
`cur_gfp_setting.site_max_page_no = 2`    
`cur_gfp_setting.site = {gfp_self_enum.SupportedWeb.Xici}`    

start to get free proxy    

`mainOp = MainOp(cur_gfp_setting, cur_gbh_setting) `       
首先清空数据库(反正都要全部重新读取网页）  
`mainOp.del_proxy()`   
检测url是否需要使用代理    
`mainOp.check_if_site_need_proxy()`    
从可以直连的网站获得代理    
`tmp_proxies = mainOp.get_proxy_without_proxy()`    
验证代理是否可用    
`first_validate_proxies = mainOp.async_validate_proxies(tmp_proxies, 'https://www.baidu.com')`    
有可用的代理，则使用这些代理，来连接需要代理连接的代理完整；否则，使用固定的cur_gbh_setting.proxy_ip    
`if len(first_validate_proxies) > 0:`    
`    tmp_proxies = mainOp.get_proxy_with_proxy(proxies=first_validate_proxies)`    
`else:`    
`    tmp_proxies = mainOp.get_proxy_with_proxy(proxies=None)`    
获得结果，再次进行验证，是否可以使用   
`second_validate_proxies = mainOp.async_validate_proxies(tmp_proxies, 'https://www.baidu.com')    `    
合并所有可用的代理    
`all_validate_proxies = first_validate_proxies+second_validate_proxies`    
`print('最终有效代理%s' % all_validate_proxies)`    
保存代理    
`mainOp.save_proxy(proxies=all_validate_proxies)`



### gfp_setting  
1. **proxy_type**    
type: ***set, element is enum=>gfp_self_enum.ProxyType***    
default: ***{gfp_self_enum.ProxyType.HIGH_ANON}***   
description:  proxy has 3 type: transparent/anonymous/high_anonymous, TRANS/ANON/HIGH_ANON. There is an addition one All, 
if set, will be replace by  TRANS+ANON+HIGH_ANON   
2. **protocol**    
type: ***set, element is enum=>gfp_self_enum.ProtocolType***
default: {gfp_self_enum.ProtocolType.HTTP, gfp_self_enum.ProtocolType.HTTPS}    
description:  proxy protocol has 4 type: HTTP, HTTPS, SOCK4, SOCK5. There is an addition one All, is set, will be replace by
HTTP+HTTPS+SOCK4+SOCK5.    
3. **country**    
type: ***set, element is enum=>gfp_self_enum.Country***    
default: {gfp_self_enum.Country.China}    
description: some web provide proxy form all countries, the parameter will filter the country. There is an addition one 
All, is set, will ignore country.    
4. **storage_type**
type: ***set, element is enum=>gfp_self_enum.StorageType***    
default: {gfp_self_enum.StorageType.All}    
description: current support 3 storage type: Mysql/Redis/File. There is an addition one All, is set, will be replace by
Mysql+Redis+File    
5. **mysql**   
type: ***dict***    
default:   
{  
'host': '127.0.0.1',  
     'port': 3306,  
     'user': 'root',  
     'pwd': '1234',  
     'db_name': 'db_proxy',  
     'tbl_name': 'tbl_proxy',  
     'charset': 'utf8mb4'     
     }    
description: if **storage_type** include Mysql, set this parameter to connect mysql.    
5. **redis**   
type: ***dict***
default:    
{    
    'host': '127.0.0.1',    
    'port': 6379,    
    'db': 0,  # 0~15    
    'pwd': None    
}     
description: if **storage_type** include Redis, set this parameter to connect redis.
6. **result_file_path**    
type: ***string***    
default: ***os.path.join(tempfile.gettempdir(), 'result.json')***     
description: if **storage_type** include File, all get proxy will be save into the file defined by **result_file_path**    
7. **valid_time_in_db**    
type: ***int***  
default: ***86400***   
unit: ***second***    
description: since all got proxy are free, not sure when these proxy will expire. So set this parameter, it a proxy expire this duration, will not delete/not_choose    
8. **site_max_page_no**    
type: ***int***    
default: ***2***   
description: min:2, max:9. The web site which provide free proxy, the content are pagationed. This parameter determine how many page 
will be handled to extract proxy.    
9. **site**    
type: ***set, enum=>gfp_self_enum.SupportedWeb***   
default: ***{gfp_self_enum.SupportedWeb.Xici}***      
description: this parameter determine which site will be used to extract proxy. currently only support 4 site:
https://www.xicidaili.com, https://www.kuaidaili.com/free, https://hidemy.name/en/proxy-list/#list, https://proxy-list.org/english.
and if All is set, will be replace by above 4 site.   

start to use    
`import get_free_proxy.main.main as main`    
`mainOp = main.MainOp(cur_gfp_setting, cur_gbh_setting)`    
delete all exist proxy   
`mainOp.del_proxy()`      
`mainOp.check_if_site_need_proxy()`   
some website that provide free proxy can connect directly       
`proxies = mainOp.get_proxy_without_proxy()`  
not all proxy are usable, so should pick up useful proxy      
`validate_proxies = mainOp.async_validate_proxies(proxies, 'https://www.baidu.com')`      
some website that provide free proxy must use proxy, use proxy get in mainOp.get_proxy_without_proxy()       
`tmp_proxies = mainOp.get_proxy_with_proxy(proxies=proxies)`    
validate usable again    
`validate_proxies += mainOp.async_validate_proxies(tmp_proxies, 'https://www.baidu.com')`      
store valid proxy to use later    
`mainOp.save_proxy(proxies=tmp_proxies)`     

### change history
0.1.0  use requests-html replace requests    
0.1.1  match gen_browser 0.1.3: when gen_header, add host base on parameter url    