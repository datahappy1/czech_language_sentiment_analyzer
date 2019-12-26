import threading
import requests
import queue
from bs4 import BeautifulSoup
from random import randint
from time import sleep

scraper_temp_output = []
scraper_final_output = []
movie_review_urls = []

czech_stopwords = ['a', 'u', 'v', 'aby', 's', 'o', 'jak', 'to', 'ale', 'za', 've', 'i', ',',
                   'ja', 'ke', 'co', 'je', 'z', 'sa', 'na', 'ze', 'ač', 'že', 'či', 'který',
                   'nějaký', 'pouze', 'bez', 'si', 'jsem', 'já', 'jí', 'by', 'asi', 'být',
                   'mi', 'je', 'jim', 'mě', 'musí', 'se', 'dnes', 'cz', 'timto', 'budes',
                   'budem', 'byli', 'jses', 'muj', 'svym', 'ta', 'tomto', 'tohle', 'tuto',
                   'tyto', 'jej', 'zda', 'proc', 'mate', 'tato', 'kam', 'tohoto', 'kdo',
                   'kteri', 'mi', 'nam', 'tom', 'tomuto', 'mit', 'nic', 'proto', 'kterou',
                   'byla', 'toho', 'protoze', 'asi', 'ho', 'nasi', 'napiste', 're', 'coz',
                   'tim', 'takze', 'svych', 'jeji', 'svymi', 'jste', 'aj', 'tu', 'tedy',
                   'teto', 'bylo', 'kde', 'ke', 'prave', 'ji', 'nad', 'nejsou', 'ci', 'pod',
                   'tema', 'mezi', 'pres', 'ty', 'pak', 'vam', 'ani', 'kdyz', 'vsak', 'ne',
                   'jsem', 'tento', 'clanku', 'clanky', 'aby', 'jsme', 'pred', 'pta', 'jejich',
                   'byl', 'jeste', 'az', 'bez', 'take', 'pouze', 'prvni', 'vase', 'ktera', 'nas',
                   'novy', 'tipy', 'pokud', 'muze', 'design', 'strana', 'jeho', 'sve', 'jine',
                   'zpravy', 'nove', 'neni\t', 'vas', 'jen', 'podle', 'zde', 'clanek', 'uz', 'email',
                   'byt', 'vice', 'bude', 'jiz', 'nez', 'ktery', 'by', 'ktere', 'co', 'nebo', 'ten',
                   'tak', 'ma', 'pri', 'od', 'po', 'jsou', 'jak', 'dalsi', 'ale', 'si', 've', 'to',
                   'jako', 'za', 'zpet', 'ze', 'do', 'pro', 'je', 'na']
czech_adjectives = ['absolutní', 'adept', 'agilní', 'agonizující', 'agresivní', 'akademický', 'akrobatický',
                    'aktivní', 'aktuální', 'alarmující', 'altruistický', 'ambiciózní', 'andělský', 'animovaný',
                    'apt', 'arid', 'arktický', 'aromatický', 'atletický', 'autentický', 'automatický',
                    'autorizovaný', 'Báječné', 'báječný', 'báječný', 'barvitý', 'bdělý', 'bdělý', 'beton',
                    'bez', 'bez', 'bezbarvé', 'bezbarvý', 'bezbranný', 'bezcenný', 'bezděčný', 'bezduchý',
                    'bezchybný', 'bezmocný', 'bezmocný', 'bezohledný', 'bezpečný', 'bezprostřední', 'bezradné',
                    'bezstarostný', 'bezvadný', 'bezvýznamný', 'bezvýznamný', 'běžný', 'bídný', 'bílý',
                    'biologicky', 'bizarní', 'bláhový', 'bland', 'blaring', 'bláznivý', 'blažený', 'bledý',
                    'blikající', 'blond', 'bobtnání', 'bohatý', 'bohatý', 'bohatý', 'bohatý', 'bohatý',
                    'bojovný', 'bolest', 'bolesti', 'bolestný', 'bouřlivý', 'brilantní', 'bronz', 'bručení',
                    'brzy', 'bzučení', 'bzučení', 'cavernous', 'celkový', 'celý', 'Celý', 'cena', 'ceněný',
                    'cenný', 'cikcak', 'cizí', 'ctěn', 'ctihodný', 'ctnostný', 'čas', 'časté', 'částečný',
                    'Černá', 'Černý', 'čerstvý', 'červenající', 'Červené', 'čilý', 'čistý', 'čistý',
                    'čtvrtletní', 'daleko', 'daleko', 'daleko', 'daleko', 'dálkový', 'další', 'další',
                    'darebák', 'darebný', 'dávání', 'definitivní', 'deliriózní', 'desetinný', 'děsivé', 'děsivý',
                    'detailní', 'dětinský', 'digitální', 'Divoké', 'divoký', 'dlouho', 'dlouhodobý', 'dobrodružný',
                    'dobrosrdečný', 'dobrotivý', 'dobrý', 'dobře', 'dobře', 'dobře', 'dobře', 'dobře', 'dobře', 'dobře',
                    'dobře-to-dělat', 'dokonalý', 'dokonalý', 'dokonce', 'dokončeno', 'domácký', 'donkichotský',
                    'dortík', 'dospělý', 'dostatek', 'dosti', 'doting', 'drahé', 'drahocenný', 'drahocenný', 'drahý',
                    'dramatický', 'dráždivý', 'drobný', 'drogy', 'droopy', 'drsný', 'drsný', 'druh', 'druhý',
                    'družstevní', 'drzý', 'dřevěný', 'důkladný', 'Důležité', 'dutý', 'důvěryhodný', 'důvěřovat',
                    'dvojče', 'dvojí', 'dvojnásobek', 'dychtivý', 'elastický', 'elegantní', 'elegantní', 'elegantní',
                    'elegantní', 'elegantní', 'elektrický', 'eliptický', 'emocionální', 'energický', 'energický',
                    'energický', 'etický', 'euforický', 'evergreen', 'exotický', 'expert', 'extatický', 'extra',
                    'extra', 'extrovertem', 'falešný', 'falešný', 'falešný', 'fantastický', 'fatální', 'fialový',
                    'firma', 'fond', 'formální', 'francouzština', 'frigidní', 'funkční', 'fuzzy', 'fyzický',
                    'gargantuovský', 'gigantický', 'grand', 'grandiózní', 'groteskní', 'gumové', 'gumovitý', 'hanebný',
                    'harmonický', 'hašteřivý', 'hbitý', 'hedvábný', 'hezké', 'bdící', 'hladký', 'hladový', 'hlasitý',
                    'hlavní', 'hlavní', 'hlavní', 'hlavní,', 'hloupě', 'hloupý', 'hloupý', 'hluboký', 'bezpečný',
                    'hlučný', 'hmatatelný', 'hnědý', 'hněvivý', 'hnijící', 'hodný', 'holý', 'horký', 'horlivý',
                    'hornatý', 'horší', 'bláznivý', 'houští', 'hovorný', 'hrabivý', 'bledý', 'hrbolatý', 'blízký',
                    'hrdý', 'hrob', 'hromový', 'hrozivý', 'hrozné', 'hrozné', 'bohatý', 'hrozný', 'hrozný', 'Hrubý',
                    'Hrubý', 'hrubý', 'hrubý', 'hrudkovitý', 'hříšný', 'budoucí', 'humongous', 'hustý', 'hvězdnatý',
                    'chabý', 'celý', 'chaotický', 'charakteristický', 'chatrný', 'chladně', 'chladný', 'chlupatý',
                    'chmurně', 'chraplavý', 'chraptivý', 'chromý', 'chudý', 'časný', 'chutný', 'Chutný', 'chybné',
                    'chytrý', 'chytrý', 'icky', 'čestný', 'idealistický', 'činný', 'idiotský', 'čistý', 'ilegální',
                    'imaginární', 'imaginativní', 'impozantní', 'indolentní', 'infantilní', 'instruktivní',
                    'inteligentní', 'ironclad', 'ironický', 'jam-packed', 'jásavý', 'jasně', 'jasně', 'Jasný', 'jasný',
                    'jedlý', 'jednoduchý', 'jednotný', 'jednotvárný', 'divoký,', 'jemný', 'jiný', 'dlouhý', 'jisté',
                    'jumbo', 'juniorský', 'dobrý', 'kajícný', 'kaleidoskopický', 'kapalina', 'katastrofální', 'každý',
                    'každý', 'klasický', 'klíč', 'klid', 'klidný', 'dokonalý', 'kloub', 'klutzy', 'kluzký', 'Kočkovitý',
                    'kolo', 'dospělý', 'komfortní', 'kompetentní', 'kompletní', 'komplex', 'konečný', 'konstantní',
                    'drahý', 'koordinované', 'kostnatý', 'košer', 'kovový', 'královský', 'královský', 'Krásná', 'drsný',
                    'krátký', 'krémová', 'kritické', 'krotit', 'kroucený', 'krutý', 'důležitý', 'křehký', 'křehký',
                    'křivý', 'dvojitý', 'který', 'kudrnatý', 'kudrnatý', 'kulaťoučký', 'kulhat', 'kultivovaný',
                    'kultivovaný', 'kůň', 'kuriózní', 'kvalifikovaný', 'květinový', 'kyselé', 'kyselý', 'Lahodné',
                    'lákavý', 'lakomý', 'lakomý', 'laskavě', 'láskyplný', 'ledový', 'legitimní', 'falešný', 'lékařský',
                    'lemováno', 'lepkavý', 'lepší', 'lesklý', 'lesklý', 'lesklý', 'lesknoucí', 'leštěné', 'letitý',
                    'levný', 'ležérní', 'limping', 'lineární', 'líný', 'líný', 'listnaté', 'livid', 'loajální',
                    'lstivý', 'hladký', 'majestátní', 'hladový', 'málo', 'hlasitý', 'malý', 'hlavní', 'mamut', 'marný',
                    'masitý', 'masivní', 'hloupý', 'mastná', 'hluboký', 'mazlivý', 'hlučný', 'měkký', 'hluchý',
                    'melodický', 'méně', 'menší', 'měsíční', 'městský', 'mezinárodní', 'milostivý', 'horký', 'milující',
                    'milý', 'miniaturní', 'hořký', 'minulost', 'mírné', 'mírné', 'hranatý', 'mladistvý', 'mladistvý',
                    'mladý', 'mléčný', 'moderní', 'modrý', 'mokré', 'mokrý', 'monstrózní', 'monstrózní', 'hrozný',
                    'monumentální', 'morální', 'hrubý', 'moudrý', 'možný', 'mrazivý', 'mrazivý', 'mrtví', 'mrzutý',
                    'mrzutý', 'mužský', 'mužský', 'nabídka', 'nabíraný', 'načechraný', 'chladný', 'nadějný', 'nádherné',
                    'nádherné', 'nádherný', 'nádherný', 'chudý,', 'nadřízený', 'náhlý', 'chutný', 'naivní', 'naivní',
                    'chytrý', 'náladový', 'naléhavé', 'náměstí', 'námořní', 'napnutý', 'naprostý', 'náročný', 'násilný',
                    'náš', 'naštvaný', 'navíjení', 'naživu', 'inteligentní', 'nebeský', 'nebezpečný', 'nebojácný',
                    'necitlivé', 'nečestný', 'nečistý', 'nedávno', 'jasný,', 'jasný,', 'jediný,', 'nedotčené',
                    'nedůležité', 'jednoduchý', 'negativní', 'negramotný', 'nehmotný', 'jemný', 'nějaký', 'nejdražší',
                    'jistý,', 'nejistý', 'nejlepší', 'několik', 'nekompatibilní', 'nekonečný', 'neloajální', 'nemocný',
                    'nemocný', 'nemotorný', 'nemovitý', 'klidný', 'nenávistný', 'neobvyklý', 'neohrožený', 'neochotný',
                    'neopatrný', 'neplodná', 'nepoctivý', 'nepodstatné', 'nepochopitelné', 'nepořádný', 'neposkvrněný',
                    'nepoužitý', 'nepraktický', 'nepraktický', 'nepravděpodobný', 'Nepravdivé', 'kouzelný',
                    'nepřekonatelný', 'nepřetržitě', 'nepřijatelný', 'nepříjemné', 'krásný', 'nepříjemný',
                    'nepřirozený', 'krátký', 'nerealistické', 'nerovný', 'krotký,', 'nervózní', 'nervózní', 'krutý',
                    'nesmazatelný', 'nesobecký', 'nesouvislé', 'nesprávně', 'křivý', 'nestabilní', 'nestálý',
                    'kudrnatý', 'nestydatý', 'neškodný', 'kulatý', 'nešťastný', 'nešťastný', 'nešťastný', 'nešťastný',
                    'neúplný', 'neuvěřitelný', 'nevědomý', 'nevhodné', 'kyselý', 'nevítané', 'lahodný', 'nevyzkoušený',
                    'lakomý', 'nevzhledný', 'nezapomenutelné', 'nezbedný', 'laskavý', 'nezbytný', 'nezdravý',
                    'nezdvořilý', 'nezkušený', 'legrační', 'lehký', 'nezodpovědný', 'nezpívaný', 'nezralý', 'nízký',
                    'nižší', 'nóbl', 'noční', 'normální', 'Nový', 'nudný', 'nudný', 'levný', 'levý', 'obarvené',
                    'obavný', 'obdélník', 'líný', 'obdélníkový', 'obdivovaný', 'obdivuhodný', 'obézní', 'oběžník',
                    'objemný', 'maličký', 'oblačno', 'oblíbený', 'oblíbený', 'malý', 'obrovský', 'obrovský', 'obrovský',
                    'obrovský', 'obrovský', 'obrovský', 'obří', 'měkký', 'obtížné', 'mělký', 'obyčejný', 'ocel',
                    'odcizený', 'oddaný', 'oddball', 'oddělený', 'odhodlaný', 'odchozí', 'odlehlé', 'odlišný', 'milý',
                    'odměňování', 'odporný', 'odporný', 'minulý', 'odpovídající', 'mírný', 'oduševnělý', 'odvážný',
                    'odvážný', 'offbeat', 'mladý', 'ohleduplný', 'moderní', 'ohlušující', 'ohromující', 'mokrý',
                    'ochotný', 'okázalý', 'okázalý', 'okouzlený', 'okouzlený', 'okouzlující', 'okouzlující',
                    'okouzlující', 'možný', 'omezený', 'opálení', 'opatrně', 'mrtvý', 'opatrný', 'opatrný', 'opečený',
                    'mužský', 'opotřebené', 'opožděný', 'optimální', 'optimistický', 'nádherný', 'opulentní',
                    'opuštěný', 'nadšený', 'opuštěný', 'oranžový', 'organické', 'originál', 'originální', 'ornery',
                    'ořechový', 'osamělý', 'osamělý', 'oslnivý', 'oslnivý', 'oslňující', 'osobní', 'ospalý', 'ostré',
                    'ostrý', 'osvícený', 'nebezpečný', 'otáčení', 'otáčení', 'otcovský', 'otevřeno', 'otravný',
                    'nedávný', 'otupělý', 'ovál', 'ověřitelný', 'ozdobný', 'nedůležitý', 'paralelní', 'parfémovaná',
                    'pastel', 'péče', 'pěkný', 'peprný', 'perfektní', 'pesimistický', 'pevný', 'pevný', 'pichlavý',
                    'pikantní', 'pilný', 'písečné', 'pískat', 'nemocný', 'plachý', 'plastický', 'platný', 'plné',
                    'nemožný', 'plodný', 'ploché', 'neobyčejný', 'plyš', 'plýtvání', 'pobavený', 'pobuřující',
                    'podezřelý', 'podhodnocené', 'podivný', 'podivný', 'podobný', 'podporující', 'podstatné',
                    'podstatný', 'nepravidelný', 'pohostinný', 'pohrdavý', 'pokorný', 'pokořit', 'pokročilý',
                    'politický', 'polovina', 'pomalý', 'pomstychtivý', 'ponížený', 'ponižující', 'ponurý', 'nervózní',
                    'popisný', 'nesmělý,', 'poslušný', 'poslušný', 'poškozené', 'nesprávný', 'potěšen', 'pouze',
                    'použitelný', 'použitý', 'povedený', 'Povinný', 'povrchní', 'povrchní', 'pozdě', 'pozitivní',
                    'poznamenal', 'neurčitý', 'pozoruhodný', 'pozoruhodný', 'pozoruhodný', 'neviditelný',
                    'pravděpodobně', 'nevinný', 'pravdivý', 'pravidelně', 'pravidelný', 'právní', 'prázdný', 'prázdný',
                    'prestižní', 'primární', 'proměnná', 'pronikavý', 'nezdvořilý', 'pronikavý', 'pronikavý',
                    'propracovaný', 'neznámý', 'prostořeký', 'prostý', 'prošedivělý', 'protiprávní', 'nízký',
                    'pruhovaný', 'průměrný', 'normální', 'První', 'nový', 'předčasně', 'nudný', 'předměstský', 'přední',
                    'přední', 'přehlíženo', 'překvapený', 'překvapující', 'přepečené', 'přeplněný', 'přeplněný',
                    'přesný', 'přesný', 'přešťastný', 'přijatelný', 'příjemný', 'příjemný', 'příjemný', 'oblíbený',
                    'příležitostně', 'Přímo', 'přímý', 'připojený', 'připraven', 'připravený', 'přírodní', 'přísný',
                    'příšerný', 'přitažlivý', 'obtížný', 'obvyklý', 'obyčejný', 'psí', 'puberťák', 'puntíkovaný',
                    'pushy', 'půvabný', 'radostný', 'radostný', 'odlišný', 'relevantní', 'rezavý', 'robustní', 'roční',
                    'roční', 'román', 'rostoucí', 'rovnat', 'rovníkový', 'rovný', 'rozbitné', 'rozbředlý', 'rozedraný',
                    'rozeklaný', 'ohromný', 'rozjařený', 'rozkošný', 'rozkošný', 'rozmazané', 'rozpustilý',
                    'rozradostněný', 'rozrušený', 'roztomilý', 'roztomilý', 'roztrhané', 'roztrhaný', 'opačný',
                    'rozumné', 'rozumný', 'rozumný', 'rozviklaný', 'rozvinuté', 'rozvláčný', 'opilý', 'rozzuřený',
                    'ruční', 'opravdový', 'Rundown', 'runny', 'rušný', 'růžový', 'růžový', 'rychle', 'rychlé', 'rychlý',
                    'rychlý', 'rychlý', 'rychlý', 'řádně', 'řezivo', 'sametový', 'samolibý', 'samostatná', 'samostatný',
                    'ospalý', 'sarkastický', 'sebejistý', 'ostrý', 'osvěžující', 'sentimentální', 'ošklivý', 'seriózní',
                    'serpentin', 'sférické', 'shadowy', 'otevřený', 'showy', 'schopný', 'silný', 'silný', 'silný',
                    'singl', 'sjednocený', 'skákání', 'skeletální', 'pečlivý,', 'skromný', 'skromný', 'skryté',
                    'skryté', 'skrytý', 'skus', 'pevný', 'skvělý', 'skvělý', 'pilný', 'slabý', 'sladký', 'sladký',
                    'Slaný', 'slaví', 'slavný', 'plný', 'slepý', 'sliznatý', 'plochý', 'složitý', 'slunný', 'slušný',
                    'smíšený', 'smoggy', 'smrtící', 'smutný', 'smutný', 'snadný', 'podivný,', 'sniveling', 'snoopy',
                    'sobecký', 'sofistikovaný', 'pohledný', 'somber', 'pohodlný', 'soucitný', 'současnost,', 'soukromé',
                    'soupy', 'sousední', 'pokročilý', 'spokojený', 'společenský', 'spolehlivý', 'pomalý', 'sporný',
                    'správně', 'srdečné', 'srdečný', 'stabilní', 'stádní', 'poslední', 'stark', 'staromódní',
                    'poškozený', 'starožitné', 'starší', 'starý', 'statečný', 'statný', 'statný', 'stejný',
                    'stimulující', 'stinné', 'strach', 'pozdní', 'strach', 'strach', 'strašidelný', 'strašidelný',
                    'strmé', 'praktický', 'stručný', 'střední', 'pravděpodobný', 'Studený', 'pravidelný', 'suchý',
                    'super', 'svárlivý', 'prázdný', 'svědomitý', 'světelné', 'světlo', 'světský', 'světský', 'syčící',
                    'sympatický', 'šedá', 'šetrný', 'Šikovný', 'provinilý', 'průběhový', 'šílený', 'široký', 'širokýma',
                    'škaredý', 'škodlivý', 'škodlivý', 'přátelský', 'šokován', 'šokující', 'španělština', 'špatně',
                    'špatně', 'špatně', 'špatný', 'špatný', 'špičatý', 'špinavý', 'špinavý', 'špinavý', 'přesný',
                    'šťastný', 'šťastný-go-šťastný', 'šťavnatý', 'štědrý', 'příjemný', 'štíhlý', 'štíhlý', 'šumivé',
                    'šupinatý', 'tajemný', 'tajný', 'tázavý', 'připravený', 'tekutina', 'přirozený', 'temný', 'temný',
                    'temperamentní', 'přitažlivý', 'temperamentní', 'přítomný', 'tento', 'teplý', 'těsný', 'testy',
                    'těžké', 'pyšný,', 'těžko', 'těžkopádný', 'těžký', 'tichý', 'tlumené', 'tlumené', 'Tlustý',
                    'tlustý', 'tónovaný', 'tragický', 'rovný', 'trim', 'rozbitý', 'tristní', 'triviální', 'trnitý',
                    'trojúhelníkový', 'trvalý', 'Třetí', 'třpytivé', 'třpytivý', 'tubby', 'tučně', 'rozrušený', 'tuhý',
                    'roztomilý', 'tvořivý', 'tvrdý', 'ty', 'týdně', 'tyto', 'rozvedený', 'ubohý', 'ubohý', 'uctíval',
                    'úctyhodný', 'rozzlobený', 'uchopení', 'uklidit', 'uklidnit', 'uklonil', 'ukotvená', 'rušný',
                    'umělecký', 'umouněný', 'úmysl', 'rychlý', 'unavený', 'unavený', 'unavený', 'únavné', 'unikátní',
                    'uplakaný', 'upozornění', 'upřímný', 'upřímný', 'upřímný', 'urážlivý', 'určitý', 'Urychlený',
                    'usedlý', 'ustaraný', 'ustaraný', 'utěšený', 'uzemněn', 'úzkost', 'úzkostlivý', 'úzký', 'uzlu',
                    'silný', 'úžasné', 'úžasný', 'úžasný', 'užitečné', 'užitečný', 'v', 'v', 'v', 'vágní', 'válcový',
                    'vapid', 'vařené', 'vařící', 'vášnivý', 'slabý', 'vážený', 'sladký', 'včas', 'slaný', 'vděčný',
                    'věčný', 'vědecké', 'slepý', 'vědět', 'vědomě', 'vědomí', 'složitý', 'veletrh', 'velkolepý',
                    'slušný', 'směšný', 'velký', 'venkovský', 'věrný', 'smutný', 'veselý', 'veselý', 'snadný', 'veselý',
                    'veselý', 'větrný', 'vibrující', 'vícebarevný', 'viditelné', 'vichřice', 'vinný', 'virtuální',
                    'vitální', 'soukromý', 'vítězný', 'vlažný', 'spící', 'vlhký', 'vlhký', 'vlnitý', 'společný',
                    'vnímavý', 'vnitřní', 'vodě', 'spravedlivý', 'volný', 'správný,', 'volný,', 'vonný', 'vrčení',
                    'vrozený', 'Všechno', 'Všeobecné', 'staromódní', 'vůně', 'starověký', 'vydatný', 'vydutý',
                    'vychrtlý', 'starý', 'vynikající', 'statečný', 'vypnuto', 'výpočet', 'stejný', 'vyrážka', 'výrobní',
                    'vysoká', 'vysoký', 'vysoký', 'vystavený', 'vystrašený', 'vyškolení', 'vyšperkovaný', 'střízlivý',
                    'využíváno', 'studený', 'výživný', 'vzácný', 'suchý', 'vzdálený', 'vzdálený', 'vzdělaný', 'vzdorný',
                    'vzpřímený', 'vzrušený', 'světlovlasý', 'světlý', 'vzrušující', 'vzrušující', 'svěží,', 'webbed',
                    'wee', 'Woozy', 'writhing', 'z', 'z', 'zábavný', 'zablácený', 'široký', 'záhadný', 'zahanbený',
                    'zájem', 'zajímavý', 'zákeřný', 'základní', 'základní', 'zákonné', 'zakřivení', 'záludný',
                    'zaměřen', 'špatný', 'zamrzlý', 'zanedbané', 'zanedbatelný', 'špinavý', 'zaplněný', 'zářící',
                    'zářivý', 'šťastný', 'zatěžující', 'zatuchlý', 'závažný', 'závislé', 'závistivý', 'štíhlý',
                    'závratný', 'zavrčel', 'Zavřeno', 'zavřít', 'zbožňoval', 'zbytečné', 'Zbytečný', 'zdobené',
                    'zdravý', 'zdrcující', 'zdvořilý', 'zdvořilý', 'zelená', 'tenký', 'zívání', 'teplý', 'zkorumpovaný',
                    'zkreslené', 'zkroucený', 'zkušený', 'zlatíčko', 'zlatý', 'zlo', 'těžký', 'tichý', 'zlomyslný',
                    'tlustý', 'zlý', 'tmavý', 'zmatený', 'znalostí', 'znamenat', 'známý', 'znát', 'znepokojen',
                    'trpělivý', 'trpný', 'znetvořený', 'zpocený', 'zpožděné', 'zpožděný', 'zralý', 'tupý', 'zrnitý',
                    'zřejmé', 'ztlumit', 'tvrdý', 'zubatý', 'typický', 'zvláštní', 'zvláštní', 'zvlněný', 'zvonění',
                    'žádný', 'žalostné', 'žalostný', 'žalostný', 'žalostný', 'žárlivý', 'že', 'že', 'ženatý', 'ženský',
                    'ženský', 'unavený', 'živý', 'živý', 'žíznivý', 'žlutá', 'žoviální']

q = queue.Queue(maxsize=0)
num_threads = 10

class Anonymize:
    def __init__(self):
        self.headers = [{'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'},
                        {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5 (.NET CLR 3.5.30729)'},
                        {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) MyAppName/1.0.0 (someone@example.com)'}]

    def randomize_request_headers(self):
        """

        :return:
        """
        return self.headers[randint(0,2)]

    @staticmethod
    def sleeper():
        """

        :return:
        """
        sleep(randint(2, 10))


def movie_review_url_collector():
    """

    :return:
    """
    start_page_urls = ['https://www.csfd.cz/zebricky/nejhorsi-filmy/?show=complete',
                       'https://www.csfd.cz/zebricky/nejlepsi-filmy/?show=complete']

    obj = Anonymize()
    for start_page in start_page_urls:
        page = requests.get(start_page, headers=Anonymize.randomize_request_headers(obj))
        soup = BeautifulSoup(page.content, 'html.parser')
        url = soup.find_all('td', attrs={'class': 'film'})
        for url_item in url:
            children = url_item.findChildren("a", recursive=False)
            movie_name = str(children).split("/")[2]
            for random_index in ([2,3,4,5,6,7,8,9,10]):
                review_page = str(random_index)
                q.put('https://www.csfd.cz/film/{}/komentare/strana-{}'.format(movie_name,review_page))
    return 0


def movie_review_scraper(q):
    """

    :param url:
    :return:
    """
    while True:
        url = q.get()
        obj = Anonymize()
        page = requests.get(url, headers=Anonymize.randomize_request_headers(obj))
        soup = BeautifulSoup(page.content, 'html.parser')
        rankings = soup.find_all('img', attrs={'class': 'rating'})
        ratings = soup.find_all('p', attrs={'class': 'post'})

        for rank, rate in zip(rankings, ratings):
            if '"odpad!"' in str(rank):
                scraper_temp_output.append({'rank': -3, 'words': ((str(rate)[17:])[:-47]).split()})
            elif '"*"' in str(rank):
                scraper_temp_output.append({'rank': -2, 'words': ((str(rate)[17:])[:-47]).split()})
            elif '"**"' in str(rank):
                scraper_temp_output.append({'rank': -1, 'words': ((str(rate)[17:])[:-47]).split()})
            elif '"***"' in str(rank):
                scraper_temp_output.append({'rank': 1, 'words': ((str(rate)[17:])[:-47]).split()})
            elif '"****"' in str(rank):
                scraper_temp_output.append({'rank': 2, 'words': ((str(rate)[17:])[:-47]).split()})
            elif '"*****"' in str(rank):
                scraper_temp_output.append({'rank': 3, 'words': ((str(rate)[17:])[:-47]).split()})

            for o in scraper_temp_output:
                for i_word in o.get('words'):
                    word = str(i_word).lower().replace('.','')
                    rank = str(o.get('rank'))
                    if word in czech_adjectives and word not in czech_stopwords:
                        scraper_final_output.append(word + ' ' + rank + '\n')
        q.task_done()


if __name__ == "__main__":

    movie_review_url_collector()
    # print(q.qsize())

    for i in range(num_threads):
        Anonymize.sleeper()

        # print(threading.active_count())
        # print(scraper_final_output)

        worker = threading.Thread(target=movie_review_scraper, args=(q,))
        worker.setDaemon(True)
        worker.start()

    q.join()

    with open('./data_temp/temp_file.txt', 'w', encoding='utf8') as fw:
        fw.writelines(scraper_output)

    print("Movie review data processing complete.")
