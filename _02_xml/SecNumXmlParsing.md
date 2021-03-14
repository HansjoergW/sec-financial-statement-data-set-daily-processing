Besonderheiten:
- in der XML Datei kann das gleiche Tag mit unterschiedlicher Präzision (Rundung) vorhanden sind.

Bsp. für Apple (10-k vom 2020)Es gibt nur wenige Fälle. Die Frage ist, ob die behandelt werdne sollten

    <us-gaap:CommercialPaper
      contextRef="i747bec89b4e84f74ae3445db3509f609_I20200926"
      decimals="-6"
      unitRef="usd">4996000000</us-gaap:CommercialPaper>
    
	<us-gaap:CommercialPaper
      contextRef="ic363a9ee75bd48f88800fc5dadba8293_I20190928"
      decimals="-6"
      unitRef="usd">5980000000</us-gaap:CommercialPaper>
    
	<us-gaap:CommercialPaper
      contextRef="i747bec89b4e84f74ae3445db3509f609_I20200926"
      decimals="-8"
      unitRef="usd">5000000000.0</us-gaap:CommercialPaper>
    
	<us-gaap:CommercialPaper
      contextRef="ic363a9ee75bd48f88800fc5dadba8293_I20190928"
      decimals="-8"
      unitRef="usd">6000000000.0</us-gaap:CommercialPaper>