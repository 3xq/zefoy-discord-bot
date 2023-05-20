import threading, requests, selenium, random, time, os, discord

from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from discord.ext import commands

bot = commands.Bot()
paths = {
	'captchaImage': '/html/body/div[5]/div[2]/form/div/div/img',
	'captchaInput': '/html/body/div[5]/div[2]/form/div/div/div/input',
	'captchaButton': '/html/body/div[5]/div[2]/form/div/div/div/div/button',
	'captchaCheck': '//*[@id="errorcapthcaclose"]/div/div',
	'viewsButton': '/html/body/div[6]/div/div[2]/div/div/div[5]/div/button',
	'viewsInput': '/html/body/div[10]/div/form/div/input',
	'viewsEnter': '/html/body/div[10]/div/form/div/div/button',
	'viewsTimer': '//*[@id="c2VuZC9mb2xeb3dlcnNfdGlrdG9V"]/span',
	'viewsExpire': '//*[@id="c2VuZC9mb2xeb3dlcnNfdGlrdG9V"]/div',
	'viewsConfirm': '//*[@id="c2VuZC9mb2xeb3dlcnNfdGlrdG9V"]/div[1]/div/form/button',
}

class tiktok:
	def __init__(self):
		self.itemid = ''
		self.uagent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'

	async def set_video_id(self, video_id):
		self.itemid = video_id

	async def setup(self):
		self.options = Options()
		self.options.add_argument('--user-agent=' + self.uagent)
		self.options.add_experimental_option('excludeSwitches', ['enable-logging'])
		self.driver = webdriver.Chrome(
			executable_path = ChromeDriverManager().install(),
			options = self.options
		)

		os.system('cls')

		self.driver.get('https://zefoy.com')
		await self.solve_captcha()

	async def sleep(self, timer):
		if 'error' in timer.lower():
			return 0, 30

		minutes = timer.split('Please wait ')[1]
		minutes = minutes.split(' minute(s)')[0]
		seconds = timer.split('minute(s) ')[1]
		seconds = seconds.split(' seconds')[0]

		return minutes, seconds

	async def online_ocr(self, image):        
		response = requests.post(
			url = 'https://api.api-ninjas.com/v1/imagetotext',
			files = {'image': image},
			headers = {
				'Origin': 'https://api-ninjas.com',
				'Referer': 'https://api-ninjas.com/'
			}
		)

		print(response)

		response = list(response.json())
		response = dict(response[0])

		return response['text']

	async def solve_captcha(self):
		while True:
			captcha = self.driver.find_element(By.XPATH, paths['captchaImage'])
			captcha.screenshot('image.png')

			with open('image.png', 'rb') as image:
				image = image.read()

			captcha = await self.online_ocr(
				bytearray(image)
			)

			print(f'[CAPTCHA][*]: TRYING CAPTCHA "{captcha}"')

			self.captcha = captcha

			WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, paths['captchaInput']))).send_keys(captcha.lower())
			WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, paths['captchaButton']))).click()

			try:
				WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, paths["captchaCheck"])))
				print(f'[CAPTCHA][-]: INCORRECT CAPTCHA "{captcha}"')

				self.driver.refresh()
			except:
				print(f'[CAPTCHA][+]: CORRECT CAPTCHA "{captcha}"')
				break

	async def start(self, ctx):
		try:
			WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, paths['viewsButton']))).click()
			await ctx.edit(content='``[VIEWS][+]: WORKING``')
		except:
			await ctx.edit(content='``[VIEWS][-]: BROKEN``')
			exit()

		os.system('cls')

		while True:
			self.driver.get('https://zefoy.com')

			WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, paths['viewsButton']))).click()
			WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, paths['viewsInput']))).send_keys(self.itemid)
			WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, paths['viewsEnter']))).click()

			try:
				time.sleep(3)

				minutes, seconds = await self.sleep(self.driver.find_element(By.XPATH, paths['viewsTimer']).text)
				await ctx.edit(content=f'``[TIMEOUT][*]: {minutes} MINUTES & {seconds} SECONDS``')

				self.timer = (int(minutes) * 60) + int(seconds)
				time.sleep(self.timer + 1)

			except Exception as exception:
				counts = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.XPATH, paths['viewsConfirm']))).text
				await ctx.edit(content=f'``[TIKTOK][*]: VIEWS {counts}``')

				WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.XPATH, paths['viewsConfirm']))).click()
				await ctx.edit(content='``[TIKTOK][+]: SENT``')
				time.sleep(5)

				minutes, seconds = await self.sleep(self.driver.find_element(By.XPATH, paths['viewsTimer']).text)
				await ctx.edit(content=f'``[TIMEOUT][*]: {minutes} MINUTES & {seconds} SECONDS``')

				self.timer = (int(minutes) * 60) + int(seconds)
				time.sleep(self.timer + 1)

		self.driver.refresh()
		self.solve()

@bot.slash_command(name = 'views', guild_ids = [])
async def views(ctx, video_id=''):
	await ctx.respond('``[*]``')

	client = tiktok()

	await client.setup()
	await client.set_video_id(video_id)
	await client.start(ctx)

bot.run('')
