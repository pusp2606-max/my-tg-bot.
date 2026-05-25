# Это список ID твоих VIP-пользователей
vip_users = {123456789} # Сюда ты будешь добавлять ID покупателей

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # Создаем клавиатуру
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="💪 Моя тренировка", callback_data="workout"))
    builder.row(types.InlineKeyboardButton(text="🔥 Купить VIP", callback_data="buy_vip"))
    
    await message.answer("Привет! Выбери действие:", reply_markup=builder.as_markup())

@dp.callback_query(lambda c: c.data == "workout")
async def process_workout(callback: types.CallbackQuery):
    # Проверяем, есть ли юзер в списке VIP
    if callback.from_user.id in vip_users:
        await callback.message.answer("Вот твоя тренировка на сегодня: ...")
    else:
        await callback.message.answer("У тебя нет VIP. Напиши владельцу: @erastxx1")

@dp.callback_query(lambda c: c.data == "buy_vip")
async def process_buy_vip(callback: types.CallbackQuery):
    await callback.message.answer("Чтобы купить VIP, напиши мне: @erastxx1")
