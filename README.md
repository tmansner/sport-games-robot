# Veikkaus pelirobotti -referenssitoteutus

Tämän dokumentin tarkoitus on kuvata 'Veikkaus pelirobotti -referenssitoteutuksen' toiminta. Kyseisen robotin tarkoituksena on kuvata ja demonstroida, kuinka automaattiset sovellukset (robotit) voivat käyttää Veikkauksen JSON-rajapintaa toiminnassaan.

## Lisenssisopimus Veikkauksen referenssitoteutuksille

[Lisenssisopimus](https://github.com/VeikkausOy/sport-games-robot/wiki/Lisenssisopimus)

## Usein kysyttyjä kysymyksiä

[UKK](https://github.com/VeikkausOy/sport-games-robot/wiki/UKK)

## Veikkauksen JSON-rajapinta

Veikkaus tarjoaa [JSON](http://en.wikipedia.org/wiki/JSON)-formaattiin perustuvan [REST](http://en.wikipedia.org/wiki/Representational_state_transfer)-rajapinnan, jonka päälle on mahdollista toteuttaa erillaisia Veikkauksen palveluja käyttäviä ohjelmia. Yksi käyttätapaus on robotit, joiden tarkoitus on pelata suuria määriä yksittäisiä pelitapahtumia Veikkauksen järjestelmään.

Alla olevat kappaleet kuvaavat ne osat Veikkauksen JSON-rajapinnasta jotka ovat oleellisia pelaamisen kannalta.

## HTTP-otsikkotietueet (Headers)

| Header | Kuvaus |
|--------|--------|
|`X-ESA-API-Key: ROBOT` | Pakollinen otsikkotietue. Automaattisilleohjelmille otsikkotietueen arvon tulee olla `ROBOT`. |
|`Content-Type: application/json`| Tietueella määritellään, että Veikkaukselle lähetettävä data tulee JSON-muodossa. |
|`Accept: application/json`| Tietueella määritellään, että Veikkaukselta tulevan vastauksen odotetaan olevan JSON-muodossa. |


Esimerkki: Arvontatietojen haku [cURL](http://curl.haxx.se/)-ohjelmalla:
```
$ curl --compressed \
    -H 'Accept: application/json' \
    -H 'Content-Type: application/json' \
    -H 'X-ESA-API-Key: ROBOT' \
	'https://www.veikkaus.fi/api/v1/sport-games/draws?game-names=MULTISCORE'
```

## Keksit (Cookies)

Jotta automaattiset ohjelmat toimisivat moitteettomasti, tulee niiden selaimen
lailla hyväksyä kaikki Veikkauksen palvelun keksit. Veikkauksen palvelun
käyttämät keksit saattavat muuttua ilman erillistä ilmoitusta, ja näin onkin
tärkeää, että ohjelmat toteutetaan niin, että ne hyväksyvät keksit ilman
erillistä määrittelyä.


Referenssi-toteutuksessa käytetään [Requests](http://docs.python-requests.org/en/latest/)-kirjastoa, joka tarjoaa automaattisen sessiohallinnan. Tämä on erittäin suositeltu tapa, koska näinollen keksien hallinta hoituu automaattisesti.


Mikäli käyttämäsi kirjasto ei tue keksien/session automaattista käsittelyä, tulee sellainen toteuttaa ohjelmaan itse.


Esimerkki: Session luominen python-kielellä käyttäen Requests-kirjastoa
```
# Vaaditut otsikkotietueet
headers = {
	'Content-type':'application/json',
	'Accept':'application/json',
	'X-ESA-API-Key':'ROBOT'
}

# Sisäänkirjautuminen Veikkauksen tilille, palauttaa sessio-objektin
def login (username, password):
	s = requests.Session()
	login_req = {"type":"STANDARD_LOGIN","login":username,"password":password}
	r = s.post("https://www.veikkaus.fi/api/v1/sessions", data=json.dumps(login_req), headers=headers)
	if r.status_code == 200:
		return s
	else:
		raise Exception("Authentication failed", r.status_code)

# Main-funktio.
# 1. Kirjautuu sisää.
# 2. Hakee monivedon tulevat kohteet (kirjautuneena käyttäjänä)
# 3. Tulostaa vastauksen
def main():
	s = login('esimerkki','salasana')
	r = s.get('https://www.veikkaus.fi/api/v1/sport-games/draws?game-names=MULTISCORE', headers=headers)
	print r.text
```


## Rajapinnan kuvaus

### Kirjautuminen

Sisäänkirjautuminen aloittaa asiakkaan session. On tärkeää, että sisäänkirjautuminen tehdään vain kerran, ja kaikki kirjautumisen vaativat pyynnöt tehdään samalla sessiolla.

Pyyntö:
```
POST /api/v1/sessions
```
Data:
```
{"type":"STANDARD_LOGIN","login":"esimerkki","password":"salasana"}
```

Vastaus:
```
JSON dokumentti, joka sisältää asiakkaan tiedot.
```


Esimerkki: Kirjautuminen sisään cURL-komennolla:
```
$ curl --compressed \
	-X POST \
	-d '{"type":"STANDARD_LOGIN","login":"esimerkki","password":"salasana"}' \
	-H 'Accept: application/json' \
	-H 'Content-Type: application/json' \
	-H 'X-ESA-API-Key: ROBOT' \
	'https://www.veikkaus.fi/api/v1/sessions'
```

Esimerkki: Kirjautuminen sisään käyttäen Requests-kirjastoa:
```
s = requests.Session()
login_req = {"type":"STANDARD_LOGIN","login":"esimerkki","password":"salasana"}
r = s.post("https://www.veikkaus.fi/api/v1/sessions", data=json.dumps(login_req), headers=headers)
reply = r.json()
print "Hello %s %s!" % (reply['firstName'], reply['lastName'])
```


### Pelikohteiden tiedot

Tällä pyynnöllä voidaan hakea pelikohteiden tiedot urheilupelikohteille,
poislukien live-veto.

Pyyntö:
```
GET /api/v1/sport-games/draws
```

Parametrit:

Pyynnölle voidaan antaa game-names -parametri, jolla voidaan määritellä vain halutut pelit. Pelien nimet ovat:

|  |  |
|-----------|----------|
|MULTISCORE | Moniveto |
|SCORE | Tulosveto |
|SPORT | Vakio |
|WINNER | Voittajavedot|
|PICKTWO | Päivän pari|
|PICKTHREE | Päivän trio|
|PERFECTA | Superkaksari|
|TRIFECTA | Supertripla|
|EBET | Pitkäveto|
|RAVI | Moniveikkaus|


Vastaus:  doc/sport-draws-reply.json

Arvonnat listatataan *draws* listassa. Lista sisältää oletuksena sekä avoimet (status OPEN) että tulevat kohteet (status FUTURE, vain Vakio). Yksittäisen pelikohteen oleellisimmat tiedot ovat sen numero *id* kentässä, sekä kuvaus *rows* listauksessa (vain avoimille pelikohteille). Kohteen kuvauksen formaatti riippuu pelistä.


Kohteen kuvauksessa pelikohde on kuvattu vaihtoehtoisesti joko *competitors*, *outcome* tai *score* listauksilla.


*competitor* listausta käytetään mm. voittajavedoissa ja moniveikkauksessa, *outcome* listausta mm. vakiossa ja pitkävedossa, ja *score* listausta mm. tulosvedossa ja monivedossa.


Esimerkki: Pelikohdetietojen haku monivetokohteille cURL-komennolla:
```
$ curl --compressed \
    -H 'Accept: application/json' \
    -H 'Content-Type: application/json' \
    -H 'X-ESA-API-Key: ROBOT' \
	'https://www.veikkaus.fi/api/v1/sport-games/draws?game-names=MULTISCORE'
```

### Pelaaminen

Pelaamiseen liittyen Veikkaus tarjoaa kaksi eri API kutsua. Ns. check-pyynnöllä
voidaan tarkistaa merkkitietojen oikeellisuus. Varsinainen pelin jättäminen
järjestelmään tapahtuu ilman '/check' osuutta URL:ssa.

Tällä pyynnöllä voidaan pelata urheilupelikohteita, poislukien live-veto.

Pyyntö:
```
POST /api/v1/sport-games/wagers/check
POST /api/v1/sport-games/wagers
```

Data:
* doc/multiscore-wager-request.json
* doc/sport-wager-request.json


Pelit lähetetään järjestelmään listana, eli useamman pelitapahtuman voi	lähettää kerralla. Tämän on myös suositeltu tapa jos tarkoituksena on pelata esimerkiksi useita yksittäisiä rivejä.


Yksittäisessä pyynnössä voi lähettää maksimissaa 25 pelitapahtumaa kerralla.


Vaikka pelit lähetetään yhdessä pyynnössä, hyväksyy järjestelmä ne yksitellen. Tämä tarkoittaa että pelit näkyvät pelitilillä yksittäisinä peliveloituksina, ja järjestelmä saattaa hylätä yksittäisen pelin (esimerkiksi rahojen loppuessa pelitililtä) muiden samassa pyynnössä olevien pelien tullessa hyväksytyksi.


Yksittäisessä pelissä oleelliset kentät ovat *drawId* ja *gameName*, sillä nämä määrittelevät mitä pelikohdetta ollaan pelaamassa. *drawId* on pelikohteen numero *id*, ja *gameName* pelin tekninen nimi (esim. SPORT). Pelin panos tulee määritellä 'stake' kenttään, mutta pelin kokonaishinnan(*price*) voi jättää halutessaan määrittelemättä. Mikäli pelin kokonaishinnan kuitenkin määrittelee, tarkistaa järjestelmä että hinta vastaa pelin oikeaa hintaa. Hinnan ollessa väärä, järjestelmä ei hyväksy pelitapahtumaa.


Pelin merkkitiedot määritellään *selections*-listaukseen, ja merkkitietojen rakenne riippuu pelistä. Esimerkiksi vakiossa merkkitiedot käytetään rakennetta, jossa valitut merkit määritellään *outcomes*-listaukseen, kun taas monivedossa käytetään *score*-elementtejä valittujen tuloksien määrittelyssä.

Vastaus: Vastauksena pelipyyntöön tulee käytännässä lähetetty JSON-data, johon on lisätty seuraavat kentät:

|Kenttä|Arvo|
|------|----|
|status | ACCEPTED/REJECTED |
|serialNumber | hyväksytyn pelin sarjanumero |
|price | pelin kokonaishinta |
| transactionTime | pelitapahtuman ajankohta |

Hylätyille peleille vastauksessa on myös *error*-elementti, joka kertoo‚ miksi peliä ei hyväksytty. Esimerkki:
```
"error":{"code":"DRAW_NOT_PLAYABLE"}
```

Esimerkki: ks. referenssitoteutus, robot.py

### Saldokysely

Tällä pyynnöllä voidaan pyytää pelitilin saldo ja tieto mahdollisista kate-
varauksista.

Pyyntö:
```
GET /api/v1/players/self/account
```

Vastaus:
Vastaus sisältää sisältää *balances* ja *CASH* elementit, joiden sisällä on sekä pelitilin saldo(*balance*) sekä mahdollisten katevarausten summa(*frozenBalance*).
```
{
	"status":"ACTIVE",
	"balances":{
		"CASH":{
			"type":"CASH",
			"balance":4200,
			"frozenBalance":0,
			"currency":"EUR"
		}
	}
}
```


Katevaraukset pyritään käsittelemään mahdollisimman pian, mutta pisimmillään niiden käsittely jää seuraavaan päivään (puolen yän jälkeen). Katevaraukseen liittyvät pelitapahtumat eivät näy pelatuissa peleissä, ja kyseisten pelitapahtumien hyväksyntä ei ole varmaa.

Pelitilin saldosta on käytettävissä vain saldon ja katevarausten erotus.

Esimerkki: saldo kysely käyttäen Requests kirjastoa
```
s = requests.Session()
login_req = {"type":"STANDARD_LOGIN","login":"esimerkki","password":"salasana"}
r = s.post("https://www.veikkaus.fi/api/v1/sessions", data=json.dumps(login_req), headers=headers)
if r.status_code == 200:
	r = s.get("https://www.veikkaus.fi/api/v1/players/self/account", headers=headers)
	j = r.json()
	print "saldo=%.2f, katevaraukset=%.2f" % (j['balances']['CASH']['balance'], j['balances']['CASH']['frozenBalance'])
else:
	print "kirjautuminen epäonnistui: " + r.text
```

### Pelatuimmuusprosentit ja Voitto-osuudet

Veikkaus tarjoaa useille peleille voitto-osuustiedot ladattavina tiedostoina. Tämä onkin suositeltava tapa aina vain kun tiedostojen käyttäminen on mahdollista.

Alla kuvaus pelatuimmuusprosenttien ja voitto-osuuksien kysymiselle Vakio
pelille.

Pyyntö:
```
	GET /api/v1/sport-games/draws/SPORT/{drawId}/popularity
	POST /api/v1/sport-games/draws/SPORT/{drawId}/winshares
```

Data/Parameterit:
Pyynnöissä {drawId} tulee korvata pelikohteen tunnisteella. ks. liite: doc/sport-winshare-request.json

Mikäli voitto-osuustietoja kysellään yli 100 kombinaation kokoiselle järjestelmälle, tulee pyynnöt pilkkoa useampaan osaan. Käytännössä jokaiseen pyyntöön lähetetään sama kombinaatio, mutta pyynnön *page*-kentällä voidaan määritellä monettako "sivua" ollaan pyytämässä.

Vastaus: ks. liite doc/sport-winshare-response.json. Vastauksen 'hasNext' kenttä kertoo onko seuraava sivu olemassa.

Monivedon kerroinlistat ladattavina tiedostoina:

|  |  |
|-----------|----------|
| Moniveto 1 | [zip](https://www.veikkaus.fi/multiscoreodds_data/moniv_1.zip) |
| Moniveto 2 | [zip](https://www.veikkaus.fi/multiscoreodds_data/moniv_2.zip) |
| Moniveto 3 | [zip](https://www.veikkaus.fi/multiscoreodds_data/moniv_3.zip) |
| Moniveto 4 | [zip](https://www.veikkaus.fi/multiscoreodds_data/moniv_4.zip) |
| Moniveto 5 | [zip](https://www.veikkaus.fi/multiscoreodds_data/moniv_5.zip) |
| Moniveto 6 | [zip](https://www.veikkaus.fi/multiscoreodds_data/moniv_6.zip) |
| Moniveto 7 | [zip](https://www.veikkaus.fi/multiscoreodds_data/moniv_7.zip) |
| Moniveto 8 | [zip](https://www.veikkaus.fi/multiscoreodds_data/moniv_8.zip) |
| Moniveto 9 | [zip](https://www.veikkaus.fi/multiscoreodds_data/moniv_9.zip) |
| Moniveto 10 | [zip](https://www.veikkaus.fi/multiscoreodds_data/moniv_10.zip) |
| Moniveto 11 | [zip](https://www.veikkaus.fi/multiscoreodds_data/moniv_11.zip) |
| Moniveto 12 | [zip](https://www.veikkaus.fi/multiscoreodds_data/moniv_12.zip) |


## Muuta

### Datan pakkaus

Veikkauksen palvelu pyrkii palauttamaan datan pakattuna aina, kun se on mahdollista. Tästä syystä palvelun käyttämistä helpottaa mikäli käytössä on kirjasto, joka osaa purkaa gzip pakatut vastaukset automaattisesti. Esimerkiksi cURL-ohjelmalla tämä onnistuu antamalla --compressed optio ohjelmalle.


Esimerkeissä käytetty Requests-kirjasto käsittelee pakatun datan automaattisesti.


Tieto siitä, onko vastaus pakattu vai ei, löytyy vastauksen HTTP otsikkotietueista:
```
	Content-Encoding: gzip
```

### Suorituskyky

Mikäli automaattiset ohjelmat tukevat moniajoa/säikeistystä, tulee rinnakkain ajettavien prosessien määrä rajoittaa maksimissaan viiteen. Tämän tulisi taata riittävän tehokas pyyntöjen käsittely, vaikka pelattavia pelejä olisi erittäin paljon. Eikä yksittäinen ohjelma näin ollen käytä kohtuuttomasti resursseja.

Kuten edellä on mainittu, tulee ohjelma hyväksyä kaikki palvelun tarjoamat keksit. Tämä on oleellista myös ohjelman suorituskyvyn kannalta.

Useamman pelipyynnön yhdistäminen yksittäiseen pyyntöön parantaa pelien hyväksyntää huomattavasti. Huomio kuitenkin, että yksittäisessä pyynnössä voi olla kerrallaan maksimissaan 25 pelitapahtumaa.
