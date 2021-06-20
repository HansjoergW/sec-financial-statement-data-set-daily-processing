## findings

unterschiedliche Werte
----------------------
0000018349-21-000014	StockRepurchaseProgramAuthorizedAmount1	us-gaap/2020	20181231	0		USD	400000000.0	150000000.0	False
0000018349-21-000014	StockRepurchaseProgramAuthorizedAmount1	us-gaap/2020	20190630	0		USD	325000000.0	725000000.0	False
0000093556-21-000008	SharesIssuedPricePerShare	us-gaap/2019	20191031	0		USD	100.0	159.45	False

Problem: für das selbe berechnete ddate gibt es mehrere Werte eigentlich müsste man hier vermutlich eher aggregrieren, als einen Wert zu lesen
0000018349-21-000014	
StockRepurchaseProgramAuthorizedAmount1	20181231	400000000.0	150000000.0	False
StockRepurchaseProgramAuthorizedAmount1	20190630	325000000.0	725000000.0	False

    ddate = 20190630
    StockRepurchaseProgramAuthorizedAmount1
      contextRef="i2f64f5d0598d4388be835ce6ff1f5222_I20190617"
      decimals="INF"
      725000000.0
    
    StockRepurchaseProgramAuthorizedAmount1
      contextRef="i768ee70f744e43e1b38017e9ce44b679_I20190616"
      decimals="INF"
      325000000.0
     
    
    ddate = 20181231
    StockRepurchaseProgramAuthorizedAmount1
      contextRef="i52b5669d12314f5097a4def1683c3e48_I20190115"
      decimals="-3"
      400000000.0
      
    StockRepurchaseProgramAuthorizedAmount1
      contextRef="i4f3448dd7e3d4832b546084cc53d8e67_I20181231"
      decimals="-3"
      150000000.0
      
    StockRepurchaseProgramAuthorizedAmount1
      contextRef="i2ca1a781e4c346519ce593e179d06dcd_I20181231"
      decimals="INF"
      25000000.0



Qrtr Calculations 2
--------------------
there seems to be an edge case
0000102729-21-000012	PaymentsForRepurchaseOfCommonStock	us-gaap/2020	20201231	26		USD	852040000.0		False
0000102729-21-000012	PaymentsForRepurchaseOfCommonStock	us-gaap/2020	20201231	27		USD		852040000.0	False


Rounding 2
----------
0000093410-21-000009	EffectiveIncomeTaxRateContinuingOperations	us-gaap/2020	20191231	4		pure	0.49	0.486	False
0000093410-21-000009	EffectiveIncomeTaxRateContinuingOperations	us-gaap/2020	20201231	4		pure	0.25	0.254	False

