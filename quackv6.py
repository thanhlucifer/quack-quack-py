import requests
import random
import time
from datetime import datetime, timedelta
from colorama import init, Fore

init(autoreset=True)
ACCESS_TOKEN = input("Vui lòng nhập ACCESS_TOKEN của bạn: ")

listCollect = []
listDuck = []
totalEgg = 0  
duckCooldowns = {}  
default_cooldown = 10  

def get_random_element(lst):
    return random.choice(lst)

def get_total_egg():
    try:
        response = requests.get(
            "https://api.quackquack.games/balance/get",
            headers={
                "authorization": f"Bearer {ACCESS_TOKEN}",
            },
            timeout=10  
        )
        if response.status_code == 200:
            res = response.json()
            global totalEgg
            for item in res['data']['data']:
                if item['symbol'] == 'EGG':
                    totalEgg = int(item['balance'])  
                    print(f"\n{Fore.GREEN}Đã thu thập được {Fore.YELLOW}{totalEgg} {Fore.GREEN}trứng\n")
        else:
            print(f"{Fore.RED}ERROR: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}Request error: {e}")
        time.sleep(1)

def get_list_reload():
    try:
        response = requests.get(
            "https://api.quackquack.games/nest/list-reload",
            headers={
                "authorization": f"Bearer {ACCESS_TOKEN}",
            },
            timeout=10  
        )
        if response.status_code == 200:
            res = response.json()
            global listCollect, listDuck
            listCollect.clear()
            if not listDuck:
                listDuck.extend(item['id'] for item in res['data']['duck'])
            
            for item in res['data']['nest']:
                if item['type_egg']:
                    listCollect.append(item['id'])
        else:
            print(f"{Fore.RED}ERROR: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}Request error: {e}")
        time.sleep(1)

def collect():
    if not listCollect:
        time.sleep(1)
        return

    egg = listCollect[0]
    try:
        response = requests.post(
            "https://api.quackquack.games/nest/collect",
            headers={
                "authorization": f"Bearer {ACCESS_TOKEN}",
                "content-type": "application/x-www-form-urlencoded",
            },
            data=f"nest_id={egg}",
            timeout=10  
        )
        
        if response.status_code == 200:
            print(f"{Fore.BLUE}{datetime.now().strftime('[%H:%M:%S]')} {Fore.GREEN}Thu thập thành công trứng {Fore.YELLOW}{egg}")
            time.sleep(2)  
            lay_egg(egg)
        elif response.status_code == 400 and "THIS_NEST_DONT_HAVE_EGG_AVAILABLE" in response.text:
            print(f"{Fore.YELLOW}Tổ chim với ID {egg} không có trứng sẵn.")
            listCollect.pop(0)
            time.sleep(1)
            collect()
        elif response.status_code == 400 and "THIS_NEST_IS_UNAVAILABLE" in response.text:
            print(f"{Fore.YELLOW}Tổ chim với ID {egg} không khả dụng. Loại bỏ tổ chim này khỏi danh sách.")
            listCollect.pop(0)
            time.sleep(1)
            collect()
        else:
            print(f"{Fore.RED}ERROR: {response.text}")
            time.sleep(1)
            collect()
    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}Request error: {e}")
        time.sleep(1)
        collect()

def lay_egg(egg):
    ready_ducks = [duck for duck in listDuck if duck not in duckCooldowns or duckCooldowns[duck] < datetime.now()]
    if not ready_ducks:
        print(f"{Fore.YELLOW}Không có con vịt nào sẵn sàng đẻ trứng.")
        time.sleep(1)
        lay_egg(egg)
        return
    duck = ready_ducks[0]  
    try:
        response = requests.post(
            "https://api.quackquack.games/nest/lay-egg",
            headers={
                "authorization": f"Bearer {ACCESS_TOKEN}",
                "content-type": "application/x-www-form-urlencoded",
            },
            data=f"nest_id={egg}&duck_id={duck}",
            timeout=10  
        )       
        if response.status_code == 200:
            global totalEgg, default_cooldown
            totalEgg += 1  
            print(f"{Fore.GREEN}Số lượng trứng hiện tại: {Fore.YELLOW}{totalEgg}")
            duckCooldowns[duck] = datetime.now() + timedelta(seconds=default_cooldown)  
            listCollect.pop(0)
            listDuck.append(listDuck.pop(0))
            collect()
        elif response.status_code == 400 and "THIS_DUCK_NOT_ENOUGH_TIME_TO_LAY" in response.text:
            print(f"{Fore.YELLOW}Con vịt với ID {duck} chưa đủ thời gian để đẻ trứng lại. Thử lại với thời gian nghỉ dài hơn.")
            duckCooldowns[duck] = datetime.now() + timedelta(seconds=default_cooldown)  
            listDuck.append(listDuck.pop(0))  
            default_cooldown += 10  
            lay_egg(egg)
        elif response.status_code == 400 and "THIS_NEST_IS_UNAVAILABLE" in response.text:
            print(f"{Fore.YELLOW}Tổ chim với ID {egg} không khả dụng. Loại bỏ tổ chim này khỏi danh sách.")
            listCollect.pop(0)
            time.sleep(1)
            collect()
        else:
            print(f"{Fore.RED}ERROR: {response.text}")
            time.sleep(1)
            lay_egg(egg)
    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}Request error: {e}")
        time.sleep(1)
        lay_egg(egg)


get_total_egg()
get_list_reload()


while True:
    get_list_reload()
    collect()
    time.sleep(2)
