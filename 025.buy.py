import pandas as pd
import datetime
import pyupbit as pb
import time

access_key='rxUYjasRKNRuBwcuxv9ZBxfunCNBgkQI4Dnaj38U'
secret_key="xELGSbu1BcUXNfGRbxg6QLmgL5cFlnNLZx0qViBQ"
upbit=pb.Upbit(access_key,secret_key)

ticker='KRW-ETH'
minute='minute60'
k=2.1
tic=1000 # tic > 1 (BTT,XEC 거래 불가)
base_KRW=1500000

def get_bb(ticker,minute,k,tic): # upper/under : 상단/하단 매수가 (Bollenger Band)
    df=pb.get_ohlcv(ticker,minute,count=20)
    upper=df.close.mean()+k*df.close.std()
    under=df.close.mean()-k*df.close.std()
    return round(upper+tic/2,1-len(str(tic*2))),round(under-tic/2,1-len(str(tic*2)))

def get_avg(ticker): # avg : 평균구매단가
    a=upbit.get_balances()
    for i in range(len(a)):
        p=list(a[i].values())
        if p[0]==ticker.split('-')[1]:
            if float(p[3])>=100:
                return round(float(p[3])) 
            else:
                return round(float(p[3]),2)
    return 0 #보유량이 없을 경우 0로 출력

def get_sell_price(ticker): # 판매금액 (sell_limit_order일 경우에만 추출 가능)
    try:
        return float(upbit.get_order(ticker,state='done')[0].get('price'))
    except:
        return 0

def get_remain_volume(ticker): # 매도주문을 넣은 구매수량
    try:
        return float(upbit.get_order(ticker)[0].get('remaining_volume'))
    except:
        return 0

def get_last_order(ticker): # ask(매도체결) bid(매수체결)
    order=upbit.get_order(ticker,state='done')[0]
    uuid=order.get('uuid')
    side=order.get('side')
    order_volume=float(order.get('price'))*float(order.get('volume'))
    return uuid,side,round(order_volume)

def print_profit(): 
    now_volume=get_remain_volume(ticker)+upbit.get_balance(ticker)
    (now_upper,now_under)=get_bb(ticker,minute,k,tic)
    print()
    print(datetime.datetime.now())
    print("보유 KRW :",round(krw),'원')
    print('보유',ticker.split('-')[1],":",round(now_volume*current_price),'원')
    print('현재 Band :',round((current_price-now_under)/(now_upper-now_under)*100),'%')
    print('이윤 :',round((Retention+remain_volume)*(current_price-avg)),'원')

def cancel_all_asks(ticker,k):
    c_uuid=upbit.get_order(ticker)
    ask_uuid=[]
    for i in range(len(c_uuid)):
        if c_uuid[i].get('side')=='ask':
            ask_uuid.append(c_uuid[i].get('uuid'))
    if len(ask_uuid)>k:
        for i in range(len(ask_uuid)):
            upbit.cancel_order(ask_uuid[i])

def get_uuid_list(u_list):
    uuid_list=[]
    for i in range(len(u_list)):
        uuid_list.append(u_list[i].get('uuid'))
    return uuid_list

def get_yet_uuid(base_uuid,ticker):
    new_uuid=get_uuid_list(upbit.get_order(ticker,state='done')[:5])
    yet_uuid=list(set(new_uuid)-set(base_uuid))
    return yet_uuid

bet_price=base_KRW*0.01
base_avg=get_avg(ticker)
try:
    base_uuid=get_uuid_list(upbit.get_order(ticker,state='done')[:5])
except:
    base_uuid=[]
# excel=pd.read_excel('BB_excel.xlsx',sheet_name='Sheet2',engine='openpyxl') # 단타투자 포트폴리오
# excel=excel.dropna()

print(datetime.datetime.now())
print('Bollenger Band 거래 시작')

while True:
    try:
        current_price=pb.get_current_price(ticker)
        (upper,under)=get_bb(ticker,minute,k,tic)
        krw=upbit.get_balance('KRW')
        Retention=upbit.get_balance(ticker)
        remain_volume=get_remain_volume(ticker)
        avg=get_avg(ticker)
        i=0

        while True: # 최초 거래중인 코인 데이터(buy) 수집
            if i*(i+1)>=avg*(Retention+remain_volume)/bet_price*2:
                buy=i+1
                break
            else:
                i+=1

        if current_price<under and krw>bet_price*1.002: # 단타 매수 타이밍:               
            upbit.buy_limit_order(ticker,current_price,bet_price*buy/current_price) #물타기
            print_profit()
            try:                
                print('Bollenger Band 매수 time.sleep(',int(minute.split('e')[1])*60,')')
                time.sleep(int(minute.split('e')[1])*60)
            except:
                print('Bollenger Band 매수 time.sleep(day)')
                time.sleep(240*60)

        if Retention+remain_volume>0 and base_avg!=avg: # 매도선 갱신
            cancel_all_asks(ticker,0)
            if upper>avg*1.002:
                upbit.sell_limit_order(ticker,round(upper+tic/2,1-len(str(tic*2))),upbit.get_balance(ticker))
            else:
                upbit.sell_limit_order(ticker,round(avg*1.002+tic/2,1-len(str(tic*2))),upbit.get_balance(ticker))
            print('Bollenger Band 매도선 갱신')

        if Retention+remain_volume>0 and current_price>upper and current_price>avg*1.002: #단타 매도 타이밍
            cancel_all_asks(ticker,0)
            upbit.sell_limit_order(ticker,current_price,Retention)
            print('Bollenger Band 매도 요청')

        # try:
        #     yet_uuid=get_yet_uuid(base_uuid,ticker)           
        #     if len(yet_uuid)==0:
        #         base_avg=get_avg(ticker)
        #     else:
        #         for i in range(len(yet_uuid)):
        #             uuid_order=upbit.get_order(yet_uuid[i])
        #             order=round(float(uuid_order.get('price'))*float(uuid_order.get('executed_volume')))
        #             now=uuid_order.get('created_at')
        #             if uuid_order.get('side')=='bid':
        #                 excel=excel.append({'index':now,'buy':order,'sell':0,'profit':0,'accprofit':0},ignore_index=True)
        #             else:
        #                 excel=excel.append({'index':now,'buy':0,'sell':order,'profit':round(order-base_avg*float(uuid_order.get('executed_volume'))),'accprofit':round(excel.profit.sum()+order-base_avg*float(uuid_order.get('executed_volume')))},ignore_index=True)
        #         excel.to_excel('BB_excel.xlsx',index=False)
        #         base_uuid=get_uuid_list(upbit.get_order(ticker,state='done')[:5])       
        # except:
        #     pass

        try:
            if buy>=14 and Retention+remain_volume>0 and minute=='minute15':
                cancel_all_asks(ticker,1)
                minute='day'
            elif buy<13 and minute=='day':
                minute='minute15'
        except:
            pass
        
        print_profit()
        time.sleep(3)
        
    except Exception as e:
        print(e)
        time.sleep(3600)