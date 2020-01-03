import random
import numpy as np
import pandas as pd

# тестовая функция
def test():
    print('working')
    
# parameters
# salary
citizen_salary_parameter1=3
citizen_salary_parameter2=10

# параметры для отбора продукта
max_price=10000
min_qv=0

# разброс расходов
max_cost=100
min_cost=5

# разброс качества
max_qv=30
min_qv=2

# разброс капитала
cap_avarage=1000
cap_disp=300

# разброс инвестиций
capital_average=-100
capital_disp=50

# разброс изменений себестоимости
cost_average=0
cost_disp=5

# разброс изменений качества
qv_average=0
qv_disp=3

# класс продукта      
class product:
    def __init__(self, id=-1, quality=-100, price=-10000):
        self.id=id
        self.quality=quality
        self.price=price
        
    # отображаем все параметры в виду dataframe
    def to_df(self):
        df=pd.DataFrame(data=[self.__dict__.values()], columns=self.__dict__.keys())
        return df
    
# класс потребителя
class citizen:
    def __init__(self, id=0):
        # id
        self.id=id
        # стартовый капитал
        self.money=self.set_salary()
    
    # задаём схему по которой человек будет получать зарплату
    # все схемы на основе генератора случайных чисел
    def set_salary(self):
        # "коммунизм", у всех одинаковое случайное число
        # return round(random.randint(10, 100),2)
        # "развитой социализм", нормальное распределение, у большиснтва средняя зарплата
        #return round(random.normalvariate((100-10)/2, 10),2)
        # "современное общество", есть длинный правый хвост
        return round(random.gammavariate(citizen_salary_parameter1, citizen_salary_parameter2),2)
        
    # функция потребления продуктов
    # берём то, что можем позволить по деньгам
    # берём самый качественный, который можем
    # при равном качестве тот, что дешевле
    def consume(self, products):
        # возвращать будем продукт
        fun_result=product(id=-1)
        available_product_lst=[]
        # цикл для фильтрации тех, что не карману
        for pr in products:
            if self.money>=pr.price:
                available_product_lst.append(pr)
        
        best_price=max_price
        best_qv=min_qv
        # цикл поиска лучшего качества
        for pr in available_product_lst:
            if pr.quality>=best_qv:
                best_qv=pr.quality
        
        product_qv_lst=[]
        # сбор всех продуктов лучшего качества
        for pr in available_product_lst:
            if pr.quality==best_qv:
                product_qv_lst.append(pr)
        
        # выбор из них тех, что дешевле
        for pr in product_qv_lst:
            if pr.price<=best_price:
                best_price=pr.price
        
        # вывод продукта с лучшими характеристиками
        for pr in product_qv_lst:
            if pr.price==best_price:
                fun_result=pr
                break
        
        return fun_result 
    
    # отображаем все параметры в виду dataframe
    def to_df(self):
        df=pd.DataFrame(data=[self.__dict__.values()], columns=self.__dict__.keys())
        return df
    
    
# класс фабрики        
class factory:
    def __init__(self, id=-1):
        # id
        self.id=id
        # предел качества продукта, меньше - можно
        self.max_quality=self.set_params()[0]
        # себестоимость
        self.cost=self.set_params()[1]
        # деньги у завода
        self.capital=self.set_params()[2]
        # продажи текущего периода
        self.pur=0
        # цена продажи текущего периода
        self.price=0
        self.capital_history=[]
        self.cost_history=[]
        self.quality_history=[]
        self.pur_history=[]
        self.price_history=[]
        self.history=pd.DataFrame()
        
    def set_params(self):
        max_quality=round(random.randint(min_qv, max_qv),0)
        selcost=round(random.randint(min_cost, max_cost),2)
        capital=round(random.normalvariate(cap_avarage, cap_disp),2)
        
        return max_quality, selcost, capital
        
    # функция проверки кредитоспособности
    def check(self):
        if self.capital<=0:
            return -1
        else:
            return 0

    #  функция производтсва
    def produce(self, product_id, price, quality):
        # если норм по капиталам, себестоимости и производственным мощностям, то вперёд
        if (price>self.cost) and (quality<=self.max_quality) and (self.check()==0):
            self.price=price
            return product(id=product_id, quality=quality, price=price)
        else:
            self.price=-10000
            return product(id=-1)
        
    # функкция сделки
    def trade(self):
        # расходы на производство считаем здесь, чтобы не заморачиваться пока остатками
        self.capital=self.capital-self.cost
        if self.check()==0:
            # поднимаем счётчики
            self.pur=self.pur+1
            self.capital=self.capital+self.price
        else:
            pass
        
    # храним историю продаж, запускаем в конце цикла
    def hist(self):#, period):
        self.capital_history.append(self.capital)
        self.cost_history.append(self.cost)
        self.quality_history.append(self.max_quality)
        self.pur_history.append(self.pur)
        self.price_history.append(self.price)
        
    def get_modern_params(self):
        capital_addon=round(random.normalvariate(capital_average, capital_disp),2)
        # костыль на случай отрицательных инвестиций
        if capital_addon>0:
            capital_addon=-10
        cost_addon=round(random.normalvariate(cost_average, cost_disp),2)
        qv_addon=round(random.normalvariate(qv_average, qv_disp),0)
        
        return qv_addon, cost_addon, capital_addon
    
    def modernise_proces(self,qv_addon, cost_addon, capital_addon):
        if (self.capital+capital_addon>0):
            if self.max_quality+qv_addon>0:
                self.max_quality=np.round(self.max_quality+qv_addon,0)
            if self.cost+cost_addon>0:
                self.cost=np.round(self.cost+cost_addon,2)
            self.capital=np.round(self.capital+capital_addon,2)
        else:
            pass
    
    # функция модернизации
    def modernise(self):
        # получили параметры модернизации
        qv_addon, cost_addon, capital_addon=self.get_modern_params()
        
        # если раунд не первый, то
        if len(self.pur_history)>1:
            # если сейчас продаж нет, а раньше были, то откатываемся
            if (self.pur_history[-1]==0)&(self.pur_history[-2]>0):
#                 print(self.id, ': 1')
                self.max_quality=self.quality_history[-2]
                self.cost=self.cost_history[-2]
            # иначе модернизируемся
            else: 
#                 print(self.id, ': 2')
                self.modernise_proces(qv_addon, cost_addon, capital_addon)
        # на первом раунде все модернизируются
        else: 
#             print(self.id, ': 3')
            self.modernise_proces(qv_addon, cost_addon, capital_addon)

    def to_null(self):
        # обнуляем счётчики текущего цикла
        self.price=0
        self.pur=0
    
    # отображаем все параметры в виду dataframe
    def to_df(self):
        df=pd.DataFrame(data=[self.__dict__.values()], columns=self.__dict__.keys())
        df=df.drop(columns=['history'])
        return df
    
# функции рынка, то есть встречи потребителей и продуктов
def global_produce(fact_lst):
    products=[]
    for f in fact_lst:
        if f.check()==0:
            product=f.produce(product_id=f.id, price=f.cost+1, quality=f.max_quality)
            products.append(product)
            
    return products

def global_consume(cit_lst, products):
    products_to_trade=[]
    for cit in cit_lst:
        product=cit.consume(products)
        products_to_trade.append(product)
        
    return products_to_trade

def global_trade(goods_to_trade, fact_lst):
    for good in goods_to_trade:
        if good.id>=0:
            fact_lst[good.id].trade()
            
def global_posttrade(fact_lst):    
    for fact in fact_lst:
        fact.hist()
        fact.to_null()
        fact.modernise()
        
    

def market_period(cit_lst, fact_lst, period):
    products_to_consume=global_produce(fact_lst)
    goods_to_trade=global_consume(cit_lst, products_to_consume)
    
    cit_df=pd.DataFrame()
    for i in range(len(goods_to_trade)):
        good=goods_to_trade[i].to_df()
        good['citizen_id']=i
        good['money']=cit_lst[i].money
        cit_df=pd.concat([cit_df, good])
        
    cit_df['period']=period
        
        
    global_trade(goods_to_trade, fact_lst)
    
    fact_df=pd.DataFrame()
    for fact in fact_lst:
        fact_df=pd.concat([fact_df, fact.to_df()])
        
    fact_df=fact_df[['id', 'max_quality', 'cost', 'capital', 'pur', 'price']]
    fact_df['period']=period
    
    global_posttrade(fact_lst)
    
    return cit_df, fact_df

def model(cit_lst, fact_lst, R):
    print('Modelling started')
    
    cit_df=pd.DataFrame()
    fact_df=pd.DataFrame()
    
    for r in range(R):
        print('Round ', r, ' started')
        cit_df_r, fact_df_r=market_period(cit_lst, fact_lst, r)
        cit_df=pd.concat([cit_df, cit_df_r])
        fact_df=pd.concat([fact_df, fact_df_r])
    
    print('Modelling finished')
        
    return cit_df, fact_df