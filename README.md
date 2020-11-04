# Veikkaus pelirobotti -referenssitoteutus

Tämän dokumentin tarkoitus on kuvata 'Veikkaus pelirobotti -referenssitoteutuksen' toiminta. Kyseisen robotin tarkoituksena on kuvata ja demonstroida, kuinka asiakkaiden automaattiset sovellukset (robotit) voivat käyttää Veikkauksen JSON-rajapintaa toiminnassaan.

## Lisenssisopimus Veikkauksen referenssitoteutuksille

[Lisenssisopimus](https://github.com/VeikkausOy/sport-games-robot/wiki/Lisenssisopimus)

## Usein kysyttyjä kysymyksiä

[UKK](https://github.com/VeikkausOy/sport-games-robot/wiki/UKK)

## Veikkauksen JSON-rajapinta

Veikkaus tarjoaa [JSON](http://en.wikipedia.org/wiki/JSON)-formaattiin perustuvan [REST](http://en.wikipedia.org/wiki/Representational_state_transfer)-rajapinnan, jonka päälle on mahdollista toteuttaa erilaisia Veikkauksen pelipalveluja käyttäviä ohjelmia. Yksi käyttötapaus on robotit, joiden tarkoitus on pelata suuria määriä yksittäisiä pelitapahtumia Veikkauksen järjestelmään.

Alla olevat kappaleet kuvaavat ne osat Veikkauksen JSON-rajapinnasta, jotka ovat oleellisia pelaamisen kannalta.

## HTTP-otsikkotietueet (Headers)

| Header | Kuvaus |
|--------|--------|
|`X-ESA-API-Key: ROBOT` | Pakollinen otsikkotietue. Automaattisille ohjelmille otsikkotietueen arvon tulee olla `ROBOT`. |
|`Content-Type: application/json`| Tietueella määritellään, että Veikkaukselle lähetettävä data tulee JSON-muodossa. |
|`Accept: application/json`| Tietueella määritellään, että Veikkaukselta tulevan vastauksen odotetaan olevan JSON-muodossa. |


Esimerkki: Arvontatietojen haku [cURL](http://curl.haxx.se/)-ohjelmalla:
```
$ curl --compressed \
    -H 'Accept: application/json' \
    -H 'Content-Type: application/json' \
    -H 'X-ESA-API-Key: ROBOT' \
	'https://www.veikkaus.fi/api/sport-open-games/v1/games/MULTISCORE/draws'
```

## Keksit (Cookies)

Jotta asiakkaiden automaattiset ohjelmat toimisivat moitteettomasti, tulee niiden, selaimen tavoin, hyväksyä kaikki Veikkauksen palvelun keksit. Veikkauksen palvelun käyttämät keksit saattavat muuttua ilman erillistä ilmoitusta, jonka vuoksi on tärkeää toteuttaa ohjelmat niin, että ne hyväksyvät keksit ilman erillistä määrittelyä.


Referenssi-toteutuksessa käytetään [Requests](http://docs.python-requests.org/en/latest/)-kirjastoa, joka tarjoaa automaattisen sessiohallinnan. Tämä on erittäin suositeltu tapa, koska näin keksien hallinta hoituu automaattisesti.

Mikäli käyttämäsi kirjasto ei tue keksien/session automaattista käsittelyä, tulee sellainen toteuttaa ohjelmaan itse.

Esimerkki: Session luominen python-kielellä käyttäen Requests-kirjastoa
```
import requests
import json

# Vaaditut otsikkotietueet
headers = {
	'Content-type':'application/json',
	'Accept':'application/json',
	'X-ESA-API-Key':'ROBOT'
}

# Sisäänkirjautuminen Veikkauksen tilille palauttaa sessio-objektin
def login (username, password):
	s = requests.Session()
	login_req = {"type":"STANDARD_LOGIN","login":username,"password":password}
	r = s.post("https://www.veikkaus.fi/api/bff/v1/sessions", data=json.dumps(login_req), headers=headers)
	if r.status_code == 200:
		return s
	else:
		raise Exception("Authentication failed", r.status_code)

# Main-funktio.
# 1. Kirjautuu sisään
# 2. Hakee Monivedon tulevat kohteet (kirjautuneena käyttäjänä)
# 3. Tulostaa vastauksen
def main():
	s = login('esimerkki','salasana')
	r = s.get('https://www.veikkaus.fi/api/sport-open-games/v1/games/MULTISCORE/draws', headers=headers)
	print(r.text)
	
main()
```


## Rajapinnan kuvaus

### Kirjautuminen

Sisäänkirjautuminen aloittaa asiakkaan session. On tärkeää, että sisäänkirjautuminen tehdään vain kerran ja kaikki kirjautumisen vaativat pyynnöt tehdään samalla sessiolla.

Pyyntö:
```
POST /api/bff/v1/sessions
```
Data:
```
{"type":"STANDARD_LOGIN","login":"esimerkki","password":"salasana"}
```

Vastaus:
```
Tyhjä JSON dokumentti.
```


Esimerkki: Kirjautuminen sisään cURL-komennolla:
```
$ curl --compressed \
	-X POST \
	-d '{"type":"STANDARD_LOGIN","login":"esimerkki","password":"salasana"}' \
	-H 'Accept: application/json' \
	-H 'Content-Type: application/json' \
	-H 'X-ESA-API-Key: ROBOT' \
	'https://www.veikkaus.fi/api/bff/v1/sessions'
```

Esimerkki: Kirjautuminen sisään käyttäen Requests-kirjastoa:
```
s = requests.Session()
login_req = {"type":"STANDARD_LOGIN","login":"esimerkki","password":"salasana"}
r = s.post("https://www.veikkaus.fi/api/bff/v1/sessions", data=json.dumps(login_req), headers=headers)
if r.status_code == 200:
	print("Login successful")
```


### Pelikohteiden tiedot

Tällä pyynnöllä voidaan hakea pelikohteiden tiedot urheilupelikohteille, poislukien live-veto.

Pyyntö:
```
GET /api/sport-open-games/v1/games/GAME/draws
```

Parametrit:

Pyynnölle annetaan games -parametri, jolla voidaan määritellä haluttu peli. Pelien nimet ovat:

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

Vastaus:  doc/sport-draws-reply.json

Arvonnat esitetaan taulukkona ja sisältää vain avoimet pelattavissa olevat kohteet. Yksittäisen pelikohteen oleellisimmat tiedot ovat sen indeksi *listIndex* ja arvontanumero *id* kentissä sekä kuvaus *rows* listauksessa (vain avoimille pelikohteille). Kohteen kuvauksen formaatti on pelikohtainen.

Kohteen kuvauksessa pelikohde on kuvattu vaihtoehtoisesti joko *competitors* tai *outcome* listauksilla.

*competitor* listausta käytetään voittajavedoissa, *outcome* listausta mm. vakiossa, tulosvedossa ja monivedossa.


Esimerkki: Pelikohdetietojen haku monivetokohteille cURL-komennolla:
```
$ curl --compressed \
    -H 'Accept: application/json' \
    -H 'Content-Type: application/json' \
    -H 'X-ESA-API-Key: ROBOT' \
	'https://www.veikkaus.fi/sport-open-games/api/v1/games/MULTISCORE/draws'
```

### Pelaaminen

Pelaamiseen liittyen Veikkaus tarjoaa kaksi eri API-kutsua. Ns. check-pyynnöllä voidaan tarkistaa merkkitietojen oikeellisuus. Varsinainen pelin jättäminen järjestelmään tapahtuu ilman '/check' osuutta URL:ssa.

Tällä pyynnöllä voidaan pelata urheilupelikohteita, poislukien live-veto.

Pyyntö:
```
POST /api/sport-interactive-wager/v1/tickets/check
POST /api/sport-interactive-wager/v1/tickets
```

Data:
* doc/multiscore-wager-request.json
* doc/sport-wager-request.json


Pelit lähetetään järjestelmään listana, eli useamman pelitapahtuman voi	lähettää kerralla. Tämän on myös suositeltu tapa jos tarkoituksena on pelata esimerkiksi useita yksittäisiä rivejä.

Yksittäisessä pyynnössä voi lähettää enintään 25 pelitapahtumaa kerralla.

Vaikka pelit lähetetään yhdessä pyynnössä, hyväksyy järjestelmä ne yksitellen. Tämä tarkoittaa, että pelit näkyvät pelitilillä yksittäisinä peliveloituksina ja järjestelmä saattaa hylätä yksittäisen pelin (esimerkiksi rahojen loppuessa pelitililtä) muiden samassa pyynnössä olevien pelien tullessa hyväksytyksi.

Yksittäisessä pelissä oleelliset kentät ovat *listIndex* ja *gameName*, sillä nämä määrittelevät, mitä pelikohdetta ollaan pelaamassa. *listIndex* on pelikohteen tiedoissa sama *listIndex*, ja *gameName* pelin tekninen nimi (esim. SPORT). Pelin panos tulee määritellä 'stake'-kenttään, mutta pelin kokonaishinnan(*price*) voi jättää halutessaan määrittelemättä. Mikäli pelin kokonaishinta kuitenkin on määritelty, järjestelmä tarkistaa, että hinta vastaa pelin oikeaa hintaa. Hinnan ollessa väärä, järjestelmä ei hyväksy pelitapahtumaa.

Pelin merkkitiedot määritellään *boards* osioon, joka on lista *betType*- ja *stake*-arvoja sekä *selections*-listaus. Merkkitietojen rakenne on pelikohtainen. Esimerkiksi Vakiossa merkkitiedoissa käytetään rakennetta, jossa valitut merkit määritellään *outcomes*-listaukseen, kun taas Tulos- ja Monivedossa käytetään *homeScores*- ja *awayScores*-elementtejä valittujen tuloksien määrittelyssä. Yhteen pelitapahumaan voi tehdä *boards* listaan xx (tbd) peliriviä kerralla hyväksyttäväksi.
 
Vastaus: Vastauksena pelipyyntöön tulee käytännässä lähetetty JSON-data, johon on lisätty mm. seuraavat kentät:

|Kenttä|Arvo|
|------|----|
|serialNumber | hyväksytyn pelin sarjanumero |
|transactionTime | pelitapahtuman aikaleima |

Hylätyille peleille vastauksessa on myös *error*-elementti, joka kertoo‚ miksi peliä ei hyväksytty. Esimerkki:
```
"error":{"code":"DRAW_NOT_PLAYABLE"}
```

Esimerkki: ks. referenssitoteutus, robot.py

### Saldokysely

Tällä pyynnöllä voidaan pyytää pelitilin saldo.

Pyyntö:
```
GET /api/v1/players/self/account
```

Vastaus:
Vastaus sisältää sisältää *balances* ja *CASH* elementit, joiden sisällä on sekä pelitilin käytettävissä oleva saldo(*usableBalance*).

Esimerkki: saldokysely käyttäen Requests kirjastoa
```
s = requests.Session()
login_req = {"type":"STANDARD_LOGIN","login":"esimerkki","password":"salasana"}
r = s.post("https://www.veikkaus.fi/api/bff/v1/sessions", data=json.dumps(login_req), headers=headers)
if r.status_code == 200:
	r = s.get("https://www.veikkaus.fi/api/v1/players/self/account", headers=headers)
	j = r.json()
	print("saldo=%.2f" % (j['balances']['CASH']['usableBalance']))
else:
	print("kirjautuminen epäonnistui: " + r.text)
```

### Pelatuimmuusprosentit ja Voitto-osuudet

Veikkaus tarjoaa vakioille ja monivedoille voitto-osuustiedot ladattavina tiedostoina. Tämä onkin suositeltava tapa aina vain kun tiedostojen käyttäminen on mahdollista.

Alla kuvaus pelatuimmuusprosenttien, kertoimien ja voitto-osuuksien kysymiselle peleille. *drawId* on kohteen tiedoista saatu arvontanumero kentästä *id*. Osa rajapinnoista on vain tietyille peleille (esim. voitto-osuudet on vain Vakiolle).

Pyyntö:
```
	GET /api/sport-odds/v1/games/SCORE/draws/{drawId}/odds
	GET /api/sport-popularity/v1/games/SPORT/draws/{drawId}/popularity
	POST /api/sport-winshares/v1/games/SPORT/draws/{drawId}/winshares
```

Data/Parameterit:
Pyynnöissä {drawId} tulee korvata pelikohteen tunnisteella. ks. liite: doc/sport-winshare-request.json

Mikäli voitto-osuustietoja kysellään yli 100 kombinaation kokoiselle järjestelmälle, tulee pyynnöt pilkkoa useampaan osaan. Käytännössä jokaiseen pyyntöön lähetetään sama kombinaatio, mutta pyynnön *page*-kentällä voidaan määritellä, monettako "sivua" ollaan pyytämässä. Vastauksen *hasNext* kenttä kertoo onko seuraava sivu olemassa.

Vastaus: 
* doc/score-odds-response.json
* doc/score-popularity-response.json
* doc/sport-popularity-response.json
* doc/sport-winshare-response.json.

Vakion voitto-osuudet ladattavina tiedostoina (arvattu lokaatio/nimi tbd):

|  |  |
|-----------|----------|
| Vakio 1 | [zip](https://www.veikkaus.fi/vakio_data/vakio_1.zip) |
| Vakio 2 | [zip](https://www.veikkaus.fi/vakio_data/vakio_2.zip) |
| Vakio 3 | [zip](https://www.veikkaus.fi/vakio_data/vakio_3.zip) |
| Vakio x | [zip](https://www.veikkaus.fi/vakio_data/vakio_x.zip) |

Huomioitava, että tiedostot ja voitto-osuuslaskuri toimivat vain Vakioille, joissa alle 15 kohdetta.

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


## Toto-pelit

Tässä esitetään lyhyesti Toto-pelien kohteiden haku ja pelaaminen.

Rajapinnassa käytettyjä termejä:
* card - tapahtuma
* race - lähtö
* runner - kilpailija
* pool - pelikohde
* odds - kertoimet

### Pelikohteiden haku

Seuraavilla kyselyillä saa listauksen ravitapahtumista.

```
GET /api/toto-info/v1/cards/today            # kuluvan päivän tapahtumat
GET /api/toto-info/v1/cards/future           # tulevien päivien tapahtumat
GET /api/toto-info/v1/cards/active           # kuluvan ja tulevien päivien tapahtumat
GET /api/toto-info/v1/cards/date/2017-04-18  # annetun päivän tapahtumat
```

Tapahtumalistauksesta löytyy myös tietoja bonus ja jackpot -rahoista. Tapahtuman tunnistetta (cardId) käytetään tapahtumaan liittyvien tietojen hakuun.

```
GET /api/toto-info/v1/card/{cardId}/pools    # tapahtuman kaikki pelikohteet
GET /api/toto-info/v1/card/{cardId}/races    # tapahtuman lähdöt
GET /api/toto-info/v1/race/{raceId}/runners  # lähdön osallistujat
GET /api/toto-info/v1/race/{raceId}/pools    # yhden lähdön pelikohteet
```

Pelikohteiden kertoimet löytyvät JSON-muodossa kyselyllä

```
GET /api/toto-info/v1/pool/{poolId}/odds      # pelikohteen kertoimet
```

T-peleihin pelatut yhdistelmät on saatavilla ainoastaan XML-muodossa. "cards.xml"-tiedostossa luetellaan kuluvan päivän kohteet sekä niihin liittyvät kerroin- ja yhdistelmätiedostot.

```
GET /api/toto-info/v1/xml/cards.xml
GET /api/toto-info/v1/xml/{n_ddmmyyyy_Rn_txx}.xml.zip
```

### Pelaaminen

Toto-pelien pelaamien etenee neljässä vaiheessa:

1. Peliehdotuksen lähetys
```
POST /api/toto-wager/v1/bet/{poolId}
```
Data: doc/t5-proposal-request.json    
Yhdessä peliehdotuksessa voi olla pelejä vain yhteen toto-pelikohteeseen. Useamman pelin yhdistäminen yhteen peliehdotukseen nopeuttaa pelien hyväksyntää merkittävästi. Pelien maksimimäärää ei ole rajoitettu, mutta palvelin voi hylätä erittäin suuria peliehdotuksia tai liian usein toistuvia yrityksiä. Peliehdotus näkyy pelitilillä yhtenä peliveloituksena. Jos pelitilin saldo ei riitä kaikkien peliehdotuksen sisältämien pelien pelaamiseen, hylätään koko peliehdotus kaikkine peleineen.

2. Peliehdotuksen tarkastuksen odottelu
```
GET /api/toto-wager/bet/{proposalId}
```
 - 200 - peliehdotuksen tarkastus kesken
 - 201 - peliehdotus tarkastettu ja tallennettu (doc/t5-proposal-response.json)

3. Peliehdotuksen pelaaminen
```
PUT /api/toto-wager/bet/{proposalId}
```
Vaiheessa 1 tarkastettu peliehdotus on tallennettu palvelimelle ja säilyy siellä korkeintaan 10 minuuttia. Jos vaihetta 3 ei aloiteta tässä ajassa, on pelaaminen aloitettava uudestaan vaiheesta 1. Useamman peliehdotuksen pelaaminen rinnakkain yhdeltä pelitililtä EI nopeuta toto-pelien hyväksyntää.

4. Pelien hyväksymisen odottelu
```
GET /api/toto-wager/ticket/{ticketId}
```
 - 200 - pelien hyväksyminen kesken, vastauksesta ilmenee, kuinka pelaaminen on edennyt
 - 201 - pelit pelattu

### Toto-pelien tuotenimet

| | |
|----|---------------|
|VOI | Toto: Voittaja|
|SIJ | Toto: Sija|
|VS | Toto: Voittaja+Sija|
|KAK | Toto: Kaksari|
|KPR | Toto: Kaksari ristiin|
|EKS | Toto: Eksakta|
|EKR | Toto: Eksakta ristiin|
|SPA | Toto: Sijapari|
|SPR | Toto: Sijapari ristiin|
|TRO | Toto: Troikka|
|TRR | Toto: Troikka ristiin|
|DUO | Toto: Päivän Duo|
|T4 | Toto: Toto4|
|T5 | Toto: Toto5|
|T54 | Toto: Toto54|
|T6 | Toto: Toto6|
|T64 | Toto: Toto64|
|T65 | Toto: Toto65|
|T7 | Toto: Toto7|
|T75 | Toto: Toto75|
|T76 | Toto: Toto76|
|T8 | Toto: Toto8|
|T86 | Toto: Toto86|
|T87 | Toto: Toto87|


## Muuta

### Datan pakkaus

Veikkauksen palvelu pyrkii palauttamaan datan pakattuna aina, kun se on mahdollista. Tästä syystä palvelun käyttämistä helpottaa mikäli käytössä on kirjasto, joka osaa purkaa gzip pakatut vastaukset automaattisesti. Esimerkiksi cURL-ohjelmalla tämä onnistuu antamalla --compressed optio ohjelmalle.


Esimerkeissä käytetty Requests-kirjasto käsittelee pakatun datan automaattisesti.


Tieto siitä, onko vastaus pakattu vai ei, löytyy vastauksen HTTP-otsikkotietueista:
```
	Content-Encoding: gzip
```

### Suorituskyky ja asiakkaiden ohjelmien toiminnallisuus sekä testaaminen

Mikäli asiakkaiden automaattiset ohjelmat tukevat moniajoa/säikeistystä, tulee rinnakkain ajettavien prosessien määrä rajoittaa enintään neljään (4). Tämän tulisi taata riittävän tehokas pyyntöjen käsittely, vaikka pelattavia pelejä olisi paljon. Näin yksittäinen ohjelma ei käytä kohtuuttomasti resursseja.

Kuten edellä on mainittu, tulee asiakkaiden ohjelmien hyväksyä kaikki palvelun tarjoamat keksit. Tämä on oleellista myös ohjelman suorituskyvyn kannalta.

Useamman pelipyynnön yhdistäminen yksittäiseen pyyntöön parantaa pelien hyväksyntää huomattavasti. Huomioi kuitenkin, että yksittäisessä pyynnössä voi olla kerrallaan maksimissaan 25 pelitapahtumaa.

Asiakkaiden ohjelmien ei kannata kysellä Veikkauksen järjestelmästä kerroinpäivityksiä alle minuutin syklillä. 

Asiakkaiden on syytä kiinnittää erityistä huomiota etenkin mahdollista rinnakkaisuutta sisältävien ohjelmiensa testaamiseen. 
Säikeet etenevät omaa tahtiaan ja mahdollisista suorituksista voi muodostua suuri joukko testattavia polkuja. Tällöin testatuksi tulee yleensä vain pieni osajoukko kaikista mahdollisista poluista. Siksi ohjelmiin jää usein virheitä, jotka johtavat ongelmiin vain tietyissä tilanteissa, ja ongelmat raportoidaan vasta, kun ohjelma on jo käytössä.
Testaamisen lisäksi myös löydettyjen virheiden korjaaminen voi olla vaikeaa. Tähän voi olla syynä esim. se, että rinnakkaiset suoritukset voivat edetä kauas varsinaisesta virheestä ennen kuin ongelmat ovat niin pahoja, että ne huomataan.
Testaustarkoituksia varten kannattaakin mahdollisuuksien mukaan lisätä apukoodia, joka auttaa virheiden jäljityksessä. Tämäkään ei valitettavasti aina riitä, sillä joskus ongelmat peittyvät, kun virheiden jäljittämistä varten lisätty apukoodi aktivoidaan.
