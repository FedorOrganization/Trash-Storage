import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
import psycopg2
import time

db_conf = {
    'user': 'your_db_user',
    'password': 'your_db_password',
    'database': 'your_database_name',
    'host': 'your_db_host',
    'port': 5432
}
TOKEN = "7014899022:AAEddAEJBNhGZsLNRqBu_JEOk1CtUp_OkTg"


class Item:
    def __init__(self, name, cost, effect, level):
        self.name = name
        self.cost = cost
        self.effect = effect
        self.level = level


class Shop:
    def __init__(self):
        self.worker_cost = 100
        self.pickaxes = [
            Item("Деревянная кирка", 50, 5, 1),
            Item("Бронзовая кирка", 100, 10, 3),
            Item("Железная кирка", 200, 20, 6),
            Item("Серебряная кирка", 400, 40, 12),
            Item("Золотая кирка", 800, 80, 24),
            Item("Платиновая кирка", 1600, 160, 48),
            Item("Алмазная кирка", 3200, 320, 96),
            Item("Титановая кирка", 6400, 640, 192),
            Item("Мифриловая кирка", 12800, 1280, 384),
            Item("Магическая кирка", 25600, 2560, 768)
        ]
        self.swords = [
            Item("Деревянный меч", 50, 10, 1),
            Item("Бронзовый меч", 100, 20, 3),
            Item("Железный меч", 200, 40, 6),
            Item("Серебряный меч", 400, 80, 12),
            Item("Золотой меч", 800, 160, 24),
            Item("Платиновый меч", 1600, 320, 48),
            Item("Алмазный меч", 3200, 640, 96),
            Item("Титановый меч", 6400, 1280, 192),
            Item("Мифриловый меч", 12800, 2560, 384),
            Item("Магический меч", 25600, 5120, 768)
        ]


class User:
    def __init__(self, gold=0, exp=0, level=1, workers=2, gold_per_sec=0, exp_per_sec=0, pickaxes=None, swords=None,
                 last_update=None):
        self.gold = gold
        self.exp = exp
        self.level = level
        self.workers = workers
        self.gold_per_sec = gold_per_sec
        self.exp_per_sec = exp_per_sec
        self.pickaxes = pickaxes if pickaxes is not None else []
        self.swords = swords if swords is not None else []
        self.last_update = last_update if last_update is not None else time.time()

    def update_resources(self):
        now = time.time()
        sec = now - self.last_update

        # Добавляем золото и опыт за прошедшее время
        self.gold += self.gold_per_sec * sec
        self.exp += self.exp_per_sec * sec

        self.last_update = now  # Обновляем время последнего обновления
        self.level_up()  # Проверяем возможность повышения уровня

    def level_up(self):
        needed_exp = self.level * 200
        if self.exp >= needed_exp:
            self.exp -= needed_exp
            self.level += 1


class MainBot:
    def __init__(self, token):
        self.bot = Bot(token)
        self.dp = Dispatcher()
        self.shop = Shop()
        self.users = {}

    async def start(self):
        self.dp.message.register(self.start_command, Command(commands=["start"]))
        self.dp.message.register(self.save_command, Command(commands=["save"]))
        self.dp.callback_query.register(self.button_click, lambda c: True)
        await self.bot.delete_webhook(drop_pending_updates=True)
        await self.dp.start_polling(self.bot)

    def get_user(self, user_id):
        if user_id not in self.users:
            self.users[user_id] = User()
        return self.users[user_id]

    async def init_db(self):
        self.conn = psycopg2.connect(**db_conf)
        self.conn.autocommit = True
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id BIGINT PRIMARY KEY,
                gold REAL DEFAULT 0,
                exp REAL DEFAULT 0,
                level INTEGER DEFAULT 1,
                gold_per_sec REAL DEFAULT 0,
                exp_per_sec REAL DEFAULT 0,
                workers INTEGER DEFAULT 2,
                pickaxes TEXT,
                swords TEXT,
                last_update REAL
            )
        ''')
        cursor.close()

    async def save_command(self, message: types.Message):
        user_id = message.from_user.id
        user = self.get_user(user_id)
        await self.save_user(user_id, user)
        await message.answer("Ваш прогресс сохранен.")

    async def save_user(self, user_id, user):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO users (id, gold, exp, level, gold_per_sec, exp_per_sec, workers, pickaxes, swords, last_update)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                gold = EXCLUDED.gold,
                exp = EXCLUDED.exp,
                level = EXCLUDED.level,
                gold_per_sec = EXCLUDED.gold_per_sec,
                exp_per_sec = EXCLUDED.exp_per_sec,
                workers = EXCLUDED.workers,
                pickaxes = EXCLUDED.pickaxes,
                swords = EXCLUDED.swords,
                last_update = EXCLUDED.last_update
        ''', (user_id, user.gold, user.exp, user.level, user.gold_per_sec, user.exp_per_sec, user.workers,
              ','.join(user.pickaxes), ','.join(user.swords), user.last_update))
        cursor.close()

    async def start_command(self, message: types.Message):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Добыча золота 💰", callback_data="gold")],
            [InlineKeyboardButton(text="Добыча опыта ✨", callback_data="exp")],
            [InlineKeyboardButton(text="Магазин 🛒", callback_data="shop")],
            [InlineKeyboardButton(text="Профиль 👤", callback_data="profile")]
        ])
        await message.answer("Выберите кнопку", reply_markup=keyboard)

    async def button_click(self, callback_query: types.CallbackQuery):
        user_id = callback_query.from_user.id
        user = self.get_user(user_id)
        user.update_resources()
        action = callback_query.data

        if action == "gold":
            await self.gold_click(callback_query, user)
        elif action == "exp":
            await self.exp_click(callback_query, user)
        elif action == "shop":
            await self.shop_menu(callback_query, user)
        elif action == "profile":
            await self.profile(callback_query, user)
        elif action == "buy_worker":
            await self.buy_worker(callback_query, user)
        elif action == "shop_pickaxes":
            await self.shop_pickaxes_menu(callback_query, user)
        elif action == "shop_swords":
            await self.shop_swords_menu(callback_query, user)
        elif action.startswith("buy_pickaxe"):
            await self.buy_pickaxe(callback_query, user, action)
        elif action.startswith("buy_sword"):
            await self.buy_sword(callback_query, user, action)

    async def gold_click(self, callback_query, user):
        if user.workers <= 0:
            await callback_query.message.answer("У вас нет рабочих")
        else:
            user.workers -= 1
            user.gold_per_sec += 10
            await callback_query.message.answer(
                f"1 рабочий отправлен на добычу золота.\n Осталось рабочих: {user.workers}"
            )

    async def exp_click(self, callback_query, user):
        if user.workers <= 0:
            await callback_query.message.answer("У вас нет рабочих")
        else:
            user.workers -= 1
            user.exp_per_sec += 20
            await callback_query.message.answer(
                f"1 рабочий отправлен на добычу опыта.\n Осталось рабочих: {user.workers}"
            )

    async def shop_menu(self, callback_query, user):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Купить рабочего 👷", callback_data="buy_worker")],
            [InlineKeyboardButton(text="Купить кирку ⛏️", callback_data="shop_pickaxes")],
            [InlineKeyboardButton(text="Купить меч ⚔️", callback_data="shop_swords")]
        ])
        await callback_query.message.answer("Добро пожаловать в магазин!", reply_markup=keyboard)

    async def profile(self, callback_query, user):
        await callback_query.message.answer(
            f"Ваш профиль 👤:\n"
            f"Уровень: {user.level}\n"
            f"Опыт: {int(user.exp)}/{user.level * 200}\n"
            f"Золото: {int(user.gold)}\n"
            f"Золото/с: {user.gold_per_sec}\n"
            f"Опыт/с: {user.exp_per_sec}\n"
            f"Рабочие: {user.workers}"
        )

    async def buy_worker(self, callback_query, user):
        if user.gold >= self.shop.worker_cost:
            user.gold -= self.shop.worker_cost
            user.workers += 1
            await callback_query.message.answer(f"Вы купили рабочего. Осталось рабочих: {user.workers}")
        else:
            await callback_query.message.answer("У вас недостаточно золота")

    async def shop_pickaxes_menu(self, callback_query, user):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"{pickaxe.name} - {pickaxe.cost} золота",
                                  callback_data=f"buy_pickaxe_{pickaxe.name}")]
            for pickaxe in self.shop.pickaxes
        ])
        await callback_query.message.answer("Выберите кирку для покупки", reply_markup=keyboard)

    async def buy_pickaxe(self, callback_query, user, action):
        pickaxe_name = action[len("buy_pickaxe_"):]
        pickaxe = next((p for p in self.shop.pickaxes if p.name == pickaxe_name), None)

        if pickaxe is None:
            await callback_query.message.answer("Кирка не найдена.")
            return

        if user.gold < pickaxe.cost:
            await callback_query.message.answer(f"Вам не хватает {pickaxe.cost - user.gold} золота.")
        elif pickaxe.name in user.pickaxes:
            await callback_query.message.answer(f"У вас уже есть {pickaxe.name}.")
        elif user.level < pickaxe.level:
            await callback_query.message.answer(f"{pickaxe.name} доступна с уровня {pickaxe.level}.")
        else:
            user.gold -= pickaxe.cost
            user.gold_per_sec += pickaxe.effect
            user.pickaxes.append(pickaxe.name)
            await callback_query.message.answer(f"Вы купили {pickaxe.name}.")

    async def shop_swords_menu(self, callback_query, user):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"{sword.name} - {sword.cost} золота", callback_data=f"buy_sword_{sword.name}")]
            for sword in self.shop.swords
        ])
        await callback_query.message.answer("Выберите меч для покупки", reply_markup=keyboard)

    async def buy_sword(self, callback_query, user, action):
        sword_name = action[len("buy_sword_"):]
        sword = next((s for s in self.shop.swords if s.name == sword_name), None)

        if sword is None:
            await callback_query.message.answer("Меч не найден.")
            return

        if user.gold < sword.cost:
            await callback_query.message.answer(f"Вам не хватает {sword.cost - user.gold} золота.")
        elif sword.name in user.swords:
            await callback_query.message.answer(f"У вас уже есть {sword.name}.")
        elif user.level < sword.level:
            await callback_query.message.answer(f"{sword.name} доступен с уровня {sword.level}.")
        else:
            user.gold -= sword.cost
            user.exp_per_sec += sword.effect
            user.swords.append(sword.name)
            await callback_query.message.answer(f"Вы купили {sword.name}.")


async def main():
    bot = MainBot(TOKEN)
    await bot.init_db()
    await bot.start()


asyncio.run(main())
