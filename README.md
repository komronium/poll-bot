# Survey Bot - So'rovnoma Boti

Aiogram 3.x asosida yaratilgan zamonaviy so'rovnoma boti.

## 🚀 Xususiyatlar

- ✅ Kanalga so'rovnoma yuborish
- ✅ Inline tugmalar bilan ovoz berish
- ✅ Real-time ovozlar soni yangilanishi
- ✅ Kanal a'zoligini tekshirish
- ✅ 2 marta ovoz berishni oldini olish
- ✅ Minimal va toza kod strukturasi

## 📁 Loyiha strukturasi

```
survey-bot/
├── config.py              # Konfiguratsiya
├── database.py            # Ma'lumotlar bazasi modellari
├── main.py                # Bot kirish nuqtasi
├── handlers/              # Handlerlar
│   ├── start.py          # Start handler
│   └── poll.py           # So'rovnoma handlerlari
├── keyboards/            # Klaviaturalar
│   └── inline.py         # Inline tugmalar
├── middlewares/          # Middlewarelar
│   └── channel_check.py  # Kanal tekshiruvi
└── services/             # Biznes logika
    └── poll_service.py   # So'rovnoma servislari
```

## 🔧 O'rnatish

1. Virtual environment yaratish:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
```

2. Kerakli paketlarni o'rnatish:
```bash
pip install -r requirements.txt
```

3. `.env` faylini yaratish va to'ldirish:
```bash
cp .env.example .env
```

`.env` faylini ochib quyidagilarni to'ldiring:
```
BOT_TOKEN=your_bot_token_from_botfather
CHANNEL_ID=@your_channel_username
ADMIN_IDS=
```

## 🏃 Ishga tushirish

```bash
python main.py
```

## 📖 Foydalanish

1. Botga `/start` yuboring
2. `/create_poll` buyrug'i bilan so'rovnoma yarating
3. So'rovnoma savolini kiriting
4. Nomzodlarni vergul bilan ajratib kiriting
5. So'rovnoma avtomatik kanalga yuboriladi

## 🎯 API

- `/start` - Botni ishga tushirish
- `/create_poll` - Yangi so'rovnoma yaratish

Kanal a'zolari so'rovnomadagi inline tugmalar orqali ovoz bera olishadi.

