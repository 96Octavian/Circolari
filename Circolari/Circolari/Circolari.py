import bs4, requests, telepot, json, sys

TOKEN = sys.argv[1]

def main(TOKEN):
    bot = telepot.Bot(TOKEN)
    base_link = 'http://liceobramante.gov.it/'
    res = requests.get('http://liceobramante.gov.it/genitori/circolari/')
    #circolari = bs4.BeautifulSoup(res.text, 'lxml')
    circolari = bs4.BeautifulSoup(res.text, 'html.parser')
    ultimo = circolari.select('article div div div div div article a')
    #messaggio = ultimo[0].string + '@nLink: ' + base_link + ultimo[0].get('href')
    ultimo = [x.string + '@nLink: ' + base_link + x.get('href') for x in ultimo]
    #ultimo = [e.encode('utf-8') for e in ultimo]
    ultimo = sorted(ultimo)

    with open('archivio.txt', 'r') as archivio:
        lines = archivio.read().splitlines()

    temp3 = [x for x in ultimo if x not in lines]
    if len(temp3) != 0:
        with open('archivio.txt', 'a') as archivio:
            for e in temp3:
                archivio.write(str(e) + "\n")
                bot.sendMessage('163329729', e.replace("@n", "\n"), parse_mode='HTML')
                bot.sendMessage('66441008', e.replace("@n", "\n"), parse_mode='HTML')
    else:
        bot.sendMessage('66441008', '<i>Nessun nuovo avviso</i>', parse_mode='HTML')
        bot.sendMessage('163329729', '<i>Nessun nuovo avviso</i>', parse_mode='HTML')

if __name__ == "__main__":
    main(TOKEN)