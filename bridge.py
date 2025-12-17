import asyncio
from flask import Flask, request, jsonify
from flask_cors import CORS
from aiogram import Bot, Dispatcher, types, F
from threading import Thread

# --- OwerCry Dev Настройки ---
API_TOKEN = '8331374919:AAFQQS2nStze8ggzPYjgo0QdDYWyWSFqBv8'
ADMIN_ID = 7369769561 # ВАШ ТЕЛЕГРАМ ID

app = Flask(__name__)
CORS(app)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Хранилище очередей
queues = {} # {sessionID: [messages]}
user_map = {} # {ADMIN_ID: current_sessionID}

@app.route('/api/send', methods=['POST'])
def to_telegram():
    data = request.json
    uid, text = data['id'], data['text']
    user_map[ADMIN_ID] = uid
    asyncio.run_coroutine_threadsafe(
        bot.send_message(ADMIN_ID, f"🔌 НОВЫЙ ТИКЕТ: {uid}\n\n{text}"), loop
    )
    return jsonify({"status": "delivered"})

@app.route('/api/receive/<uid>', methods=['GET'])
def from_telegram(uid):
    msgs = queues.get(uid, [])
    queues[uid] = []
    return jsonify(msgs)

@dp.message()
async def handle_admin_reply(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        uid = user_map.get(ADMIN_ID)
        if uid:
            if uid not in queues: queues[uid] = []
            queues[uid].append(message.text)
            await message.answer(f"✅ ОТВЕТ ОТПРАВЛЕН ПОЛЬЗОВАТЕЛЮ {uid}")

def run_flask():
    app.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    Thread(target=run_flask).start()
    print("[OwerCry AI] Протокол связи активен...")
    loop.run_until_complete(dp.start_polling(bot))
