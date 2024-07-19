import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
import time

token = "7014899022:AAEddAEJBNhGZsLNRqBu_JEOk1CtUp_OkTg"

class User:
    def __init__(self):
        self.gold = 0  # Золото
        self.exp = 0  # Опыт
        self.level = 1  # Уровень
        self.workers = 2  # Рабочие
        self.gold_per_sec = 0  # Золото в секунду
        self.exp_per_sec = 0  # Опыт в секунду
        self.last_update = time.time()  # Время последнего обновления

    def update_resources(self):
        now = time.time()
        sec = now - self.last_update

        self.gold += self.gold_per_sec * sec
        self.exp += self.exp_per_sec * sec

        self.last_update = now
        self.level_up()

    def level_up(self):
        needed_exp = self.level * 200
        while self.exp >= needed_exp:
            self.exp -= needed_exp
            self.level += 1
            needed_exp = self.level * 200

class GameBot:
    def __init__(self, token):
        self.bot = Bot(token)
        self.dp = Dispatcher()
        self.users = {}  # Словарь для хранения пользователей
        self.update_interval = 5  # Интервал обновления ресурсов (в секундах)
        self.gold_effect = 5  # Начальный бонус золота в секунду при улучшении кирки
        self.exp_effect = 10  # Начальный бонус опыта в секунду при улучшении меча
        self.worker_cost = 100  # Стоимость рабочего

    async def start(self):
        self.dp.message.register(self.start_command, Command(commands=["start"]))
        self.dp.callback_query.register(self.button_click, lambda c: True)
        await self.bot.delete_webhook(drop_pending_updates=True)
        asyncio.create_task(self.update_resources_loop())
        await self.dp.start_polling(self.bot)

    async def update_resources_loop(self):
        while True:
            for user in self.users.values():
                user.update_resources()
            await asyncio.sleep(self.update_interval)

    def get_user(self, user_id):
        if user_id not in self.users:
            self.users[user_id] = User()
        return self.users[user_id]

    async def start_command(self, message: types.Message):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Добыча золота 💰", callback_data="gold")],
            [InlineKeyboardButton(text="Добыча опыта ✨", callback_data="exp")],
            [InlineKeyboardButton(text="Магазин 🛒", callback_data="shop")],
            [InlineKeyboardButton(text="Профиль 👤", callback_data="profile")]
        ])
        await message.answer("Основное меню", reply_markup=keyboard)

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
        elif action == "upgrade_pickaxe":
            await self.upgrade_pickaxe(callback_query, user)
        elif action == "upgrade_sword":
            await self.upgrade_sword(callback_query, user)

    async def gold_click(self, callback_query, user):
        if user.workers <= 0:
            await callback_query.message.answer("У вас нет рабочих")
        else:
            user.workers -= 1
            user.gold_per_sec += 10
            await callback_query.message.answer(
                f"1 рабочий отправлен на добычу золота.\nОсталось рабочих: {user.workers}"
            )
        await callback_query.answer()  # Обрабатываем запрос

    async def exp_click(self, callback_query, user):
        if user.workers <= 0:
            await callback_query.message.answer("У вас нет рабочих")
        else:
            user.workers -= 1
            user.exp_per_sec += 20
            await callback_query.message.answer(
                f"1 рабочий отправлен на добычу опыта.\nОсталось рабочих: {user.workers}"
            )
        await callback_query.answer()  # Обрабатываем запрос

    async def shop_menu(self, callback_query, user):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Купить рабочего 👷", callback_data="buy_worker")],
            [InlineKeyboardButton(text="Улучшить кирку ⛏️", callback_data="upgrade_pickaxe")],
            [InlineKeyboardButton(text="Улучшить меч ⚔️", callback_data="upgrade_sword")]
        ])
        await callback_query.message.answer("Добро пожаловать в магазин!", reply_markup=keyboard)
        await callback_query.answer()  # Обрабатываем запрос

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
        await callback_query.answer()  # Обрабатываем запрос

    async def buy_worker(self, callback_query, user):
        if user.gold >= self.worker_cost:
            user.gold -= self.worker_cost
            user.workers += 1
            self.worker_cost *= 2  # Увеличиваем стоимость следующего рабочего

            # Создаем клавиатуру и обновляем сообщение
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Купить рабочего 👷", callback_data="buy_worker")],
                [InlineKeyboardButton(text="Улучшить кирку ⛏️", callback_data="upgrade_pickaxe")],
                [InlineKeyboardButton(text="Улучшить меч ⚔️", callback_data="upgrade_sword")]
            ])
            await callback_query.message.edit_text(
                f"Вы купили рабочего. Осталось рабочих: {user.workers}",
                reply_markup=keyboard
            )
        else:
            await callback_query.message.answer(f"Вам не хватает {int(self.worker_cost - user.gold)} золота.")

        await callback_query.answer()  # Обрабатываем запрос

    async def upgrade_pickaxe(self, callback_query, user):
        cost = self.gold_effect * 10
        if user.gold < cost:
            await callback_query.message.answer(f"Вам не хватает {int(cost - user.gold)} золота.")
        else:
            user.gold -= cost
            user.gold_per_sec += self.gold_effect
            self.gold_effect *= 2
            await callback_query.message.answer(f"Вы улучшили свою кирку. Теперь золото в секунду: {user.gold_per_sec}")
        await callback_query.answer()  # Обрабатываем запрос

    async def upgrade_sword(self, callback_query, user):
        cost = self.exp_effect * 10
        if user.gold < cost:
            await callback_query.message.answer(f"Вам не хватает {int(cost - user.gold)} золота.")
        else:
            user.gold -= cost
            user.exp_per_sec += self.exp_effect
            self.exp_effect *= 2
            await callback_query.message.answer(f"Вы улучшили свой меч. Теперь опыт в секунду: {user.exp_per_sec}")
        await callback_query.answer()  # Обрабатываем запрос

bot = GameBot(token)
asyncio.run(bot.start())
