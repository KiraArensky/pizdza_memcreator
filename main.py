# Импорт библиотек
import os
import time
import traceback

try:
    import cowsay
    import sqlite3
    import requests
    import telebot
    from PIL import Image, ImageDraw, ImageFont
except ModuleNotFoundError as e:
     os.system("pip install cowsay")
     os.system("pip install sqlite3")
     os.system("pip install pyTelegramBotAPI")
     os.system("pip install pillow")
     os.system("pip install requests")
     import telebot
     import cowsay
     import sqlite3
     import requests
     from PIL import Image, ImageDraw, ImageFont


bot = telebot.TeleBot('6320016102:AAFgpkd95Wwb2_RWP52SVZ5wcwYBV7XBQ_4')  # токен бота из BotFather

print(cowsay.get_output_string('turtle', "Бот запущен!"))  # это для проверки что бот запустился
print(" " * 10, "##" * 12)
print("", end='\n')


def text_up(cur, con, message):
    pic_name = cur.execute(f'''SELECT pic FROM users_mem WHERE id = {message.chat.id}''').fetchone()[0]
    text = message.text
    cur.execute(f'''UPDATE users_mem SET text_up = '{text}' WHERE id = {message.chat.id} ''')
    con.commit()
    pic = Image.open(pic_name)

    size = 40
    font = ImageFont.truetype('fonts/Attractive-Heavy.ttf', size=size)

    width, height = pic.size

    # ascent, descent = font.getmetrics()

    w_text = font.getmask(text).getbbox()[2]
    # h_text = font.getmask(text).getbbox()[3] + descent

    line_height = sum(font.getmetrics())

    font_image = Image.new('L', (w_text, line_height))
    ImageDraw.Draw(font_image).text((0, 0), text, fill=255, font=font)
    font_image = font_image.rotate(0, resample=Image.BICUBIC, expand=True)

    x = (width - w_text) // 2
    y = int(height * 0.01)

    for i in range(3):
        pic.paste((0, 0, 0), (x - i, y), mask=font_image)
        pic.paste((0, 0, 0), (x + i, y), mask=font_image)
        pic.paste((0, 0, 0), (x, y + i), mask=font_image)
        pic.paste((0, 0, 0), (x, y - i), mask=font_image)
        pic.paste((0, 0, 0), (x - i, y + i), mask=font_image)
        pic.paste((0, 0, 0), (x + i, y + i), mask=font_image)
        pic.paste((0, 0, 0), (x - i, y - i), mask=font_image)
        pic.paste((0, 0, 0), (x + i, y - i), mask=font_image)
    pic.paste((255, 255, 255), (x, y), mask=font_image)

    os.remove(pic_name)
    pic.save(pic_name, quality=95)

    return pic_name


def text_down(cur, con, message):
    pic_name = cur.execute(f'''SELECT pic FROM users_mem WHERE id = {message.chat.id}''').fetchone()[0]
    text = message.text
    cur.execute(f'''UPDATE users_mem SET text_up = '{text}' WHERE id = {message.chat.id} ''')
    con.commit()
    pic = Image.open(pic_name)

    size = 40
    font = ImageFont.truetype('fonts/Attractive-Heavy.ttf', size=size)

    width, height = pic.size

    # ascent, descent = font.getmetrics()

    w_text = font.getmask(text).getbbox()[2]
    # h_text = font.getmask(text).getbbox()[3] + descent

    line_height = sum(font.getmetrics())

    font_image = Image.new('L', (w_text, line_height))
    ImageDraw.Draw(font_image).text((0, 0), text, fill=255, font=font)
    font_image = font_image.rotate(0, resample=Image.BICUBIC, expand=True)

    x = (width - w_text) // 2
    y = height - int(height * 0.1)

    for i in range(3):
        pic.paste((0, 0, 0), (x - i, y), mask=font_image)
        pic.paste((0, 0, 0), (x + i, y), mask=font_image)
        pic.paste((0, 0, 0), (x, y + i), mask=font_image)
        pic.paste((0, 0, 0), (x, y - i), mask=font_image)
        pic.paste((0, 0, 0), (x - i, y + i), mask=font_image)
        pic.paste((0, 0, 0), (x + i, y + i), mask=font_image)
        pic.paste((0, 0, 0), (x - i, y - i), mask=font_image)
        pic.paste((0, 0, 0), (x + i, y - i), mask=font_image)
    pic.paste((255, 255, 255), (x, y), mask=font_image)

    os.remove(pic_name)
    pic.save(pic_name, quality=95)

    return pic_name


def send_mem(user_id):
    # Подключение к БД
    con = sqlite3.connect("database/chats.db")
    # Создание курсора
    cur = con.cursor()

    cur.execute(f'''UPDATE id SET key = 'defolt' WHERE id = {user_id} ''')
    con.commit()

    pic_name = cur.execute(f'''SELECT mem FROM users_mem WHERE id = {user_id}''').fetchone()[0]
    pic = open(pic_name, 'rb')

    bot.send_photo(user_id, photo=pic, caption="Готово! @pizdza_memcreator_bot")

    os.remove(pic_name)


@bot.message_handler(commands=['start'])  # запуск бота
def start(message):
    # Подключение к БД
    con = sqlite3.connect("database/chats.db")
    # Создание курсора
    cur = con.cursor()
    # Выполнение запроса и получение всех результатов в виде списка
    result = cur.execute("""SELECT id FROM id""").fetchall()
    id_list = [elem[0] for elem in result]
    chatid = message.chat.id  # переменная для сохранения айди чата

    # добавляем айди и имя в базу данных
    if chatid not in id_list:
        cur.execute(
            f'''INSERT INTO id (id, name, key) VALUES({chatid}, '{message.from_user.first_name}', 'defolt') ''')
        cur.execute(
            f'''INSERT INTO users_mem (id) VALUES({chatid}) ''')
        con.commit()
    bot.send_message(chatid,
                     text='Хаю хай, с вами [{}](tg://user?id={})!\n\n'
                          'При помощи команды /mem_create ты сможешь создать мем!'.format(message.from_user.first_name,
                                                                                          message.from_user.id))


@bot.message_handler(commands=['mem_create'])
def mem_create(message):
    # Подключение к БД
    con = sqlite3.connect("database/chats.db")
    # Создание курсора
    cur = con.cursor()

    bot.send_message(message.chat.id, text='Пришли картинку для мема')

    cur.execute(f'''UPDATE id SET key = 'pic' WHERE id = {message.chat.id} ''')
    con.commit()


@bot.message_handler(commands=['no_text'])
def no_text(message):
    # Подключение к БД
    con = sqlite3.connect("database/chats.db")
    # Создание курсора
    cur = con.cursor()

    flag = cur.execute(f'''SELECT key FROM id WHERE id = {message.chat.id}''').fetchone()[0]

    if flag == "text_up":
        cur.execute(f'''UPDATE id SET key = 'text_down' WHERE id = {message.chat.id} ''')
        con.commit()

        bot.send_message(message.chat.id, text='Тогда отправь текст, который будет снизу, иначе пропиши /no_text\n'
                                               '\nНапример\n\n')
    elif flag == "text_down":
        send_mem(message.chat.id)


@bot.message_handler(content_types=['text'])
def text_message(message):
    # Подключение к БД
    con = sqlite3.connect("database/chats.db")
    # Создание курсора
    cur = con.cursor()

    flag = cur.execute(f'''SELECT key FROM id WHERE id = {message.chat.id}''').fetchone()[0]

    if flag == "text_up":
        pic_name = text_up(cur, con, message)
        cur.execute(f'''UPDATE users_mem SET pic = '{pic_name}' WHERE id = {message.chat.id} ''')
        cur.execute(f'''UPDATE id SET key = 'text_down' WHERE id = {message.chat.id} ''')
        con.commit()

        bot.send_message(message.chat.id, text='Отправь текст, который будет снизу, иначе пропиши /no_text\n'
                                               '\nНапример\n\n')
    elif flag == "text_down":
        pic_name = text_down(cur, con, message)
        cur.execute(f'''UPDATE users_mem SET mem = '{pic_name}' WHERE id = {message.chat.id} ''')
        con.commit()
        send_mem(message.chat.id)


@bot.message_handler(content_types=['photo'])
def pic_message(message):
    # Подключение к БД
    con = sqlite3.connect("database/chats.db")
    # Создание курсора
    cur = con.cursor()

    chatid = message.chat.id  # переменная для сохранения айди чата

    flag = cur.execute(f'''SELECT key FROM id WHERE id = {chatid}''').fetchone()[0]

    if flag == "pic":
        file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        src = 'database/' + file_info.file_path
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        im = Image.open(new_file.name)
        position = (0.05 * im.width, im.height - im.height * 0.1)
        font = ImageFont.truetype('fonts/Attractive-Heavy.ttf', size=10, encoding="unic")
        draw_text = ImageDraw.Draw(im)
        draw_text.text(
            position,
            '@pizdza_memcreator_bot',
            font=font,
            fill='#1C0606'
        )
        os.remove(new_file.name)
        im.save(new_file.name, quality=95)

        cur.execute(f'''UPDATE users_mem SET pic = '{new_file.name}' WHERE id = {message.chat.id} ''')
        cur.execute(f'''UPDATE id SET key = 'text_up' WHERE id = {message.chat.id} ''')
        con.commit()

        bot.send_message(message.chat.id, text='Отправь текст, который будет сверху, иначе пропиши /no_text\n'
                                               '\nНапример\n\n')


def telegram_polling():
    try:
        bot.polling()
    except requests.exceptions.ReadTimeout:
        bot.send_message(-633607298, text="restart bot")
        traceback_error_string = traceback.format_exc()
        with open("Error.Log", "a") as myfile:
            myfile.write("\r\n\r\n" + time.strftime("%c") + "\r\n<<ERROR polling>>\r\n" + traceback_error_string
                         + "\r\n<<ERROR polling>>")
        bot.stop_polling()
        time.sleep(10)
        telegram_polling()


if __name__ == '__main__':
    telegram_polling()
