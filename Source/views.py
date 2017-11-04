#O pacote django.shortcuts agrega funções e classes auxiliares, a função render combina
#uma dado template com um dado dicionário de dados e retorna um objeto HttpResponse.
from django.shortcuts import render
from django.http import HttpResponse

from django.views.decorators.http import require_http_methods
from .models import Greeting
import telegram
from django.views.decorators.csrf import csrf_exempt
import json
import requests
from bs4 import BeautifulSoup
from unicodedata import normalize


@csrf_exempt
# Create your views here.
@require_http_methods(["GET", "POST"])
def index(request):
    bot = telegram.Bot(token='362204380:AAHTIZzZdZacTltb2MrA17lw0ToJsY-BCCY')
    update = telegram.update.Update.de_json(json.loads(request.body),bot)
    if update.message.text == "/start":
        bot.sendMessage(chat_id=update.message.chat_id, text = "Digite a cidade seguida por hífem e o estado para saber o tempo: \nExemplo: SaoPaulo-SP")
    else:
        update = telegram.update.Update.de_json(json.loads(request.body),bot)
        #tratamento de String
        nome = update.message.text
        novo = update.message.text

        novo =   novo .replace(' ','')#retirando espaços

        novo = normalize('NFKD', novo ).encode('ASCII','ignore').decode('ASCII')#retirando acentos

        uf = novo [-2:]
        cidade = novo [:-3]

        update.message.text = 'http://www.tempoagora.com.br/previsao-do-tempo/' + uf + '/' + cidade + '/'

        site = requests.get(update.message.text)
        soup = BeautifulSoup(site.content, 'html.parser')
        titulo = soup.find_all("title")[0].get_text()
        temperatura = soup.find_all("span")[5].get_text()
        sensacao = soup.find_all("span")[7].get_text()
        velocidade = soup.find_all("span")[9].get_text()
        pressao = soup.find_all("span")[11].get_text()
        umidade = soup.find_all("span")[13].get_text()
        update.message.text = "" + titulo +"\n"+ nome+"\nTemperatura: "+temperatura+"\nSesação: "+sensacao+"\nVelocidade do Vento: "+velocidade +"\nPressão: "+pressao +"\nUmidade: "+umidade

        #Tratamento de erro - ARRUMAR
        if umidade == '%':
            bot.sendMessage(chat_id=update.message.chat_id, text = "Cidade não encontrada\nDigite a cidade seguida por hífem e o estado para saber o tempo: \nExemplo: SaoPaulo-SP")
        else:
            bot.sendMessage(chat_id=update.message.chat_id, text = update.message.text)

    return render(request, 'index.html')

def db(request):

    greeting = Greeting()
    greeting.save()

    greetings = Greeting.objects.all()

    return render(request, 'db.html', {'greetings': greetings})
