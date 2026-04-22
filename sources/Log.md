Uppdateringar

2026-02-11-Programeringslektion. 
Idag har jag fixat en server till multiplayer spelet Jag har också gjort events i servern för att folk joinar lämnar och sickar meddelanden till servern. Sedan lade jag till en funktion som kan hantera alla medelanden från klienterna på servern. Jag gjorde även en spelar klass,enemy klass och en lobby klass. Sedan lade jag till 2 Maps i servern för spelare och lobbys. När spelaren ansluter så blir deet direkt kopplade med en instans av klassen player då kan jag kolla data medans servern pratar med klienten. I Spelaren lde jag till så det visar en svart ruta samt jag kodade in i dem att de ansluter till servern och skriver ut sitt andvändarnamn som servern gav i konsolen. Nästa steg blir en meny där man kan välja att joina lobbys för att starta spelet.


2026-02-13-Hemma. 
Denna gång utvecklade jag en sak för att gå med i lobbys men jag blev inte rioktigt färdig. Detta gjorde jag genom att lägga till en funktion i klassen serverhandler för python och försöke skriva ut JASON meddelandet i servern. En så länge har jag bara fått det i vad som ser ut som hexa decimal.

2026-02-13-Ai-Letion. 
Denna lektion fokuserade jag på server kod nu kan man lägga till lobbys och se spelarna i lobbyn med deras andvändarnam och möjligheten att veta vem som var du. Det gör att jag snart kan göra en meny i klienten som gör så du kan starta spelet med dina vänner.

2026-02-25-Programeringslektion
Denna lektion har jag fixat så att clienten försöker ansluta till servern 5 gånger om det inte går. Sedan ger den upp och klagar på ditt internet. Sedan har jag även tagit och gjort så att servern kan ha en lobby stänga den och starta spelet när en spelare vill det. Då sickas hala kartan till spelarna och servern börjar sicka allas positioner. Till alla spelare i lobbyn. I slutet av lektionen kollar jag på hemsidor på hur man kan rita en 3d raycastad miljö på skärmen.

2026-03-04-Programering
Denna lektionen så fixade jag så man kan se med ett raycast perspektiv och gjorde att servern rör dig i konstant fart framåt på x axeln.

2026-03-04-Hemma
Denna gång fick jag raycasting att funngera med något som jonathan kallar fisheye effect. Jag vet inte vad det kommer ifrån sedan fixade jag också buggen med att servern aldrig sickade vart alla var eller något sådant. Så nu gör servern det varje 100 milisekunder. Nu kan jag äntligen synka spelarna i samma lobby.Jag gjorde även kartan mycket större och lade till väggar.

2026-03-11-Hemma
Denna stund så lade jag till logick som gjorde att jag kunde röra mig gennom att tryck w och s. Server blev lagig av att jag gjorde detta. Det löste jag med bara sicka input från spelaren när den ändras. Om den inte har ändrats finns den redan på servern och behöver inte sickas igen. Det verkar vara någon kanstig sak som lite roterar mig medans jag går men det får jag lösa sedan.

2026-03-18-Programeringslektionen
Denna lektion hade jag stora probelm med att python inte gick att få fungerande. Det lyckades jag lösa. Sedan så tog jag bort fisheye effect med att ta cosinus av radianen av min ratoation gånger 0,005 och gånger n som är distansen som strålen som sickades är. Sedan var det ws som vart inverterade så fixade koden genom att bytta plats på minustecknena.

2026-03-18/19-EngelskaLektion/Hemma
I dennna sektion så gjorde jag att man går in i en väg och stanar direckt. JAg hade väldigt mycket problem med detta när jag gjorde det tackvare att jag glömde att göra this istället för self i javascript. Eftersom du inte ska kunna fuska så kör all movment kod på servern. Jag har även ett anticheet på server som jag lade till för att man inte ska kunna fuska med input men detta lade jag till för ett par lektioner sedan. 

2026-03-20-AI/Hemma
I denna sektion så gjorde jag bättre och mjukare rörelse när man trycker a och d så rör jag mig på ett trevligt sätt runt och w och s går fram och bak på ett mjukare sätt. Jag har även uppdaterat servern så att den tar bort spelaren om de har kopplat bort. Om en lobby är tomm så stänger servern ner dens spelloop och tar bort den ur minnet.

2026-04-15-Programeringslektion
På dennna lektion så skulle man göra ett qize på objektorenterad programering på det quizet så fick jag 13/15 rätt. Men det ska jag ta efter detta. På spelet idag har jag gjort det som jag har prokrastinerat mest av allt. Det är UI för serverar så man kan se vilka man kan joina och sitt andvändarnamn och starta spelet. Jag har börjat lite på det och gjort fungerande så att man kan se alla lobbys som var men ännu har jag inte hunnit göra en knapp som skapar en lobby. Sedan ska jag också göra ett system som kanske låter dig byta andvändarnamn och en skärm för en lobby som man är i som ej startat spelet ännu. På servern har jag nu gjort att istället för ett ping medelande så sickar servern viktig information som klienten behöver eller är bra att ha beroende på klientens situation så man både inte blir disconcted och kan få reda på infon uttan att sicka onödiga frågor.

2026-04-15-AI Lektionen/Hemma
Denna lektion så hade jag gjort klart det man skulle göra i förtid så jag jabbade på UI. Jag lade till så att man nu kan hålla på med fönstret även när spelet ansluter till servern. Spelet upptecker nu om det mislyckas med server anslutning och vissar det för andvändaren. Spelat har nu en lista med alla lobbys som för tillfälet inte kör spelet så man kan klicka och joina. JAg lade även till en skärm för att du är i lobbyn men spelet är inte startat. Den tabben har en lista på alla spelare i lobbys som ser lika ut för alla spelare. När man ser den listan så är det en annan färg på den spelare. När man trycker start så startar den för alla. Sennare pllanaerar jag lägga till så alla kan se varandra och spela tillsamas samt lägga till någon form av mål i spelet.

2026-04-22 ProgrameringsLektion
IDag lade jag till spelar rendering som fungerar bra och du kan se spelare när de ska vara synliga men inte annars. Detta hade jag problem med eftersom spelaren ska vara kortare en väggarna och ha ett huvud. Till min hjälp tog jag då gemeni för att förklara matten bakom vad jag behövde göra så att jag kunnde implementera lösningen själv. Nu förstår jag hur den fungerar. Jag lade även till så att det är svart långt bort och ljust nära spalaren med högre render distens. ännu har jag inte fått det att fungera på spelaren men det kommer nog strax. Jag ska även fixa knappen för att lämmna lobby så den fungerar när man trycker på den.