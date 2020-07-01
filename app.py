import discord
import requests
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# .env file, local environment vars
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN') # bot client token
GUILD = os.getenv('DISCORD_GUILD') # discord server name
CHANNEL = int(os.getenv('DISCORD_CHANNEL')) # target channel id
URL = os.getenv('MMOGA_LINK') # mmoga as sales website
FILE_NAME = 'offers.txt'

client = discord.Client()

def get_offers():
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    
    weekend_offers = soup.findAll(True, { 'class':'container', 'class' : 'preorderCont' })
    #print(weekend_offers, end='\n'*2)

    message = "**MMOGA: Neue Top Deals**\n\n"

    for offer in weekend_offers:
        
        ## left offer side ##
        # here we have just one offer
        link = URL + offer.find('a')['href']
        title = offer.find('p', class_='title').text
        oldPrice = offer.find('del', class_='oldPreis').text
        newPrice = offer.find('span', class_='newPreis').text

        # build message
        message = message + build_message(title, newPrice, oldPrice, link)

        ## right offer side ##
        rightOffers = offer.select('.preR li')
        
        # here we have multiple offers, so loop
        for rightOffer in rightOffers:
            link = URL + rightOffer.find('a')['href']
            title = rightOffer.find('h4').text
            oldPrice = rightOffer.find('del').text
            newPrice = rightOffer.find('p').text

            # build message
            message = message + build_message(title, newPrice, oldPrice, link)

    return message

def build_message(title, newPrice, oldPrice, link):
    message = ''
    message = message + '**' + title + '**' + ' (' + newPrice + ' ~~' + oldPrice.replace("UVP ", "") + '~~)' + '\n'            
    message = message + 'Link: ' + link
    message = message + '\n\n'
    return message

def has_changes(currentOffers):
    f = open(FILE_NAME, 'r')
    fContent = f.read()
    f.close();

    return currentOffers != fContent

def write_changes(currentOffers):
    f = open(FILE_NAME, 'w')
    f.write(currentOffers)
    f.close()

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

    guild = discord.utils.get(client.guilds, name=GUILD)    
    channel = guild.get_channel(CHANNEL)
    message = get_offers()
   
    if (has_changes(message)):
        print('New Offers!')
        write_changes(message)
        await channel.send(message)

    os._exit(os.EX_OK)

client.run(TOKEN)