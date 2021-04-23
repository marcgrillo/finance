import time
#import os
#import execfile

good=0

for iterazione in range(1,1440):
    #import itera
    #execfile('itera.py')
    #os.system("itera.py")
    #!/usr/bin/python
    ########### Python 2.7 #############
    import http.client, urllib.request, urllib.parse, urllib.error, base64, re
    import matplotlib as mpl
    mpl.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    import time
    from matplotlib.ticker import MultipleLocator, FormatStrFormatter

    # major and minor plot seetings
    majorLocator = MultipleLocator(200)
    majorFormatter = FormatStrFormatter('%d')
    minorLocator = MultipleLocator(50)

    majoryLocator = MultipleLocator(10)
    majoryFormatter = FormatStrFormatter('%d')
    minoryLocator = MultipleLocator(2)

    majorXLocator = MultipleLocator(24)
    majorXFormatter = FormatStrFormatter('%d')
    minorXLocator = MultipleLocator(6)

    def history(a):

        body = a[2:-4]
        closeprice = []

        for key in body:
           if "Close" in key:
               c = key.split(':')
               close = float(re.findall('\d+\.\d+', c[1] )[0])
               closeprice.append(close) 

        return closeprice

    def moving_average(x, n, type='simple'):
        """
        compute an n period moving average.

        type is 'simple' | 'exponential'

        """
        x = np.asarray(x)
        if type == 'simple':
            weights = np.ones(n)
        else:
            weights = np.exp(np.linspace(-1., 0., n))

        weights /= weights.sum()

        a = np.convolve(x, weights, mode='full')[:len(x)]
        a[:n] = a[n]
        return a

    def plotcoin(closeprice):

        # create Bitcoin plot
        ema50 = moving_average(closeprice, 2, type='exponential')
        fig, ax1 = plt.subplots()
        ax1.plot(closeprice[-10:] , 'g-')
        ax1.plot(ema50[-10:] , 'r-') 
        ax1.set_title('Bitcoin Price Etoro') 
        ax1.set_xlabel('Time (1 Hour)', color='k')
        ax1.set_ylabel('Close price (USD)', color='k')
        ax1.tick_params(colors='k')
        ax1.grid(color='k', linestyle='-', linewidth=0.5)
        ax1.yaxis.set_major_locator(majorLocator)
        ax1.yaxis.set_major_formatter(majorFormatter)
        ax1.yaxis.set_minor_locator(minorLocator)
        ax1.xaxis.set_major_locator(majorXLocator)
        ax1.xaxis.set_major_formatter(majorXFormatter)
        ax1.xaxis.set_minor_locator(minorXLocator)
        plt.savefig('bitcoin.png')   # save the figure to file
        plt.close(fig)    # close the figure


    conn = http.client.HTTPSConnection('candle.etoro.com')
    # 480 is 480 periods of 1 hour, 100000 is Bitcoin
    conn.request("GET", "/candles/asc.json/OneMinute/1001/2")
    response = conn.getresponse()
    data = response.read()
    #print(type(data))
    data=data.decode("utf-8")
    a = data.split(',')
    closeprice = history(a)
    closeprice2=closeprice[0:len(closeprice)-1]
    conn.close()
    
    closeprice=[]
    for h in range(int(len(closeprice2)/23)):
        closeprice.append(closeprice2[h*23])


    #SCELGO UN RANGE: VOGLIO ANALIZZARE DA 2 A 30 INTERVALLI DA 7 MINUTI
    #SCRIVO OGNI PERIODO IN UNA LISTA DI ARRAY
    #IL PERIODO PRESO E' SEMPRE L'ULTIMO DISPONIBILE
    l_int=7
    rang=[2,5]
    num_int=rang[1]-rang[0]
    arr=[]
    for i in range(rang[0],rang[1]+1):
        arr.append(closeprice[len(closeprice)-l_int*i:len(closeprice)])

    #DIVIDO IL PERIODO PIU GRANDE I DATI IN INTERVALLI DA 7 MINUTI PER INIZIALIZZARE IL CALCOLO DEI K
    #Nota che l'ultimo valore e' quello ignoto da stimare
    import numpy as np
    inte=l_int
    num_int_tot=5
    periodo_max=closeprice[len(closeprice)-inte*num_int_tot+1:len(closeprice)]
    mat=[]
    for i in range(0,num_int_tot):
        mat.append(periodo_max[i*inte:(i+1)*inte])




    #SCRIVO IL CODICE DI ANALISI PER IL FIT LINEARE
    #UTILIZZERO' IL METODO DEI MINIMI QUADRATI
    #SOSTANZIALMENTE PER VALUTARE IL VALORE CENTRALE A CUI TENDE IL VALORE MEDIO DELLE MEDIE DEI K FACCIO UN FIT LINEARE
    #PER UN PEZZO DI DATI VIA VIA SEMPRE PIU GRANDE.
    #DEFINISCO POI IL VALORE CENTRALE COME LA MEDIA PESATA DEI VALORI DI FIT DANDO PIU IMPORTANZA (QUADRATICO) AI DATI ULTIMI PIU VICINI
    #AL VALORE DA STIMARE
    import matplotlib.pyplot as plt
    from scipy.optimize import curve_fit
    #defining the fit function
    chi_values=[]
    medie=[]
    for ind in range(num_int):
        def lin_function(x, a, b):
            return b+a*x
        lungh=len(arr[ind])
        x=np.arange(0,lungh,1)
        y=np.asarray(arr[ind])
        pars, covm = curve_fit(lin_function, x, y)
        chisq2 = ((y - lin_function(x, pars[0],pars[1]))**2).sum()
        ndof = len(y)-1
        chisq_norm=chisq2/ndof
        medie.append(pars[0]/(ind+1)**2)
        y1=pars[1]+pars[0]*x
        chi_values.append(chisq_norm)

    media_di_fit=np.mean(medie)




    #INIZIALIZZO IL CALCOLO DEI K E DEI K PESATI
    media_medie_k=[]
    for j in range(0,num_int_tot-1):
        mezzo=int((len(mat[j])-1)/2)
        x0=mat[j][mezzo]
        temp=[]
        for i in range(1,mezzo+1):
            temp.append((mat[j][mezzo+i]-mat[j][mezzo-i]))
        media_medie_k.append(np.mean(temp))


    nuova=[]
    for i in range(len(media_medie_k)):
        nuova.append(media_medie_k[i]*(i+1))
    media_medie_k_pesati=np.mean(nuova)



    #QUI STO: PRENDENDO LA MEDIA DELLE MEDIE DEI K PER OGNI INTERVALLO E STO VEDENDO QUANTO SI DISCOSTA DAL VALORE CENTRALE
    #CHE HO STIMATO ESSERE DEFINITO SECONDO UN ALGORITMO SPIEGATO SOPRA.
    #CALCOLO IL VALORE PREDETTO DI X_3 IMPONENDO IL VALORE CHE DOVREBBE AVERE AFFINCHE LA MEDIA DELLE MEDIE DEI K, COMPRESO DUNQUE
    #ANCHE L'ULTIMO INTERVALLO CHE CONTIENE IL VALORE DA STIMARE, SIA UGUALE AL VALORE CENTRALE DATO DAL FIT.
    lungheza=len(nuova)
    media_medie_k_pesati_updated=media_di_fit
    #media_medie_k_pesati_updated=(media_medie_k_pesati*lungheza+ultima_media)/lungheza+1
    #media_medie_k_pesati_updated*(lungheza+1)=media_medie_k_pesati*lungheza+ultima_media
    ultima_media=media_medie_k_pesati_updated*(lungheza+1)-media_medie_k_pesati*lungheza

    mezzo=int((len(mat[num_int_tot-1])-1)/2)
    k1=mat[num_int_tot-1][mezzo+1]-mat[num_int_tot-1][mezzo-1]
    k2=mat[num_int_tot-1][mezzo+2]-mat[num_int_tot-1][mezzo-2]
    k_3=(ultima_media*mezzo-2*k2-k1)/3
    x_meno3=mat[num_int_tot-1][2*mezzo]
    x_pred=k_3+x_meno3
    #print(x_pred)
    if (x_pred>mat[num_int_tot-1][mezzo+2]):
        val=1
        #print('Sale')
    else: 
        val=0
        #print('Scende')
    
    
    
    
    
    
    

    time.sleep(1380)
    #import checker
    #execfile('checker.py')
    #os.system("checker.py")
    
    
    
    
    #!/usr/bin/python
    ########### Python 2.7 #############
    import http.client, urllib.request, urllib.parse, urllib.error, base64, re
    import matplotlib as mpl
    mpl.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    import time
    from matplotlib.ticker import MultipleLocator, FormatStrFormatter

    # major and minor plot seetings
    majorLocator = MultipleLocator(200)
    majorFormatter = FormatStrFormatter('%d')
    minorLocator = MultipleLocator(50)

    majoryLocator = MultipleLocator(10)
    majoryFormatter = FormatStrFormatter('%d')
    minoryLocator = MultipleLocator(2)

    majorXLocator = MultipleLocator(24)
    majorXFormatter = FormatStrFormatter('%d')
    minorXLocator = MultipleLocator(6)

    def history(a):

        body = a[2:-4]
        closeprice = []

        for key in body:
           if "Close" in key:
               c = key.split(':')
               close = float(re.findall('\d+\.\d+', c[1] )[0])
               closeprice.append(close) 

        return closeprice

    def moving_average(x, n, type='simple'):
        """
        compute an n period moving average.

        type is 'simple' | 'exponential'

        """
        x = np.asarray(x)
        if type == 'simple':
            weights = np.ones(n)
        else:
            weights = np.exp(np.linspace(-1., 0., n))

        weights /= weights.sum()

        a = np.convolve(x, weights, mode='full')[:len(x)]
        a[:n] = a[n]
        return a

    def plotcoin(closeprice):

        # create Bitcoin plot
        ema50 = moving_average(closeprice, 2, type='exponential')
        fig, ax1 = plt.subplots()
        ax1.plot(closeprice[-10:] , 'g-')
        ax1.plot(ema50[-10:] , 'r-') 
        ax1.set_title('Bitcoin Price Etoro') 
        ax1.set_xlabel('Time (1 Hour)', color='k')
        ax1.set_ylabel('Close price (USD)', color='k')
        ax1.tick_params(colors='k')
        ax1.grid(color='k', linestyle='-', linewidth=0.5)
        ax1.yaxis.set_major_locator(majorLocator)
        ax1.yaxis.set_major_formatter(majorFormatter)
        ax1.yaxis.set_minor_locator(minorLocator)
        ax1.xaxis.set_major_locator(majorXLocator)
        ax1.xaxis.set_major_formatter(majorXFormatter)
        ax1.xaxis.set_minor_locator(minorXLocator)
        plt.savefig('bitcoin.png')   # save the figure to file
        plt.close(fig)    # close the figure


    conn = http.client.HTTPSConnection('candle.etoro.com')
    # 480 is 480 periods of 1 hour, 100000 is Bitcoin
    conn.request("GET", "/candles/asc.json/OneMinute/1001/2")
    response = conn.getresponse()
    data = response.read()
    #print(type(data))
    data=data.decode("utf-8")
    a = data.split(',')
    closeprice = history(a)
    closeprice=closeprice[0:len(closeprice)-1]
    conn.close()

    if (closeprice[len(closeprice)-1]-closeprice[len(closeprice)-2]>0):
        val_ver=1
        #print('Sale')
    else: 
        val_ver=0
        #print('Scende')
        
        
        
        
        
        
        
        

    if val==val_ver: good=good+1
    perc_succ=good/iterazione
    print('Iterazione numero'+str(iterazione))
    print('\nPercentuale di successo:'+str(perc_succ))