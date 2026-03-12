# ============================================================
# SOSYAL MEDYA POST SABLONLARI
# TikTok & Instagram icin hazir icerik sablonlari
# ============================================================

CHAT_SCENARIOS = {
    "mia": [
        {
            "name": "gece_mesaji",
            "conversation": [
                {"type": "incoming", "text": "Heyy... uyudun mu? 🥺", "delay": 800},
                {"type": "pause", "delay": 2000},
                {"type": "incoming", "text": "Bütün gün seni bekledim ama yazmadın...", "delay": 1500},
                {"type": "pause", "delay": 2500},
                {"type": "incoming", "text": "Neyse, sana bir şey göstermek istiyorum ama...", "delay": 1800},
                {"type": "pause", "delay": 1500},
                {"type": "incoming", "text": "Hazır mısın? 😏", "delay": 1000},
                {"type": "pause", "delay": 2500},
                {"type": "incoming", "text": "Süreli fotoğraf gönderiyorum... 📸🔥", "delay": 2000},
                {"type": "pause", "delay": 3000},
                {"type": "incoming", "text": "Beğendin mi tatlım? Sadece sana özel çektim...", "delay": 1800},
                {"type": "pause", "delay": 2000},
                {"type": "incoming", "text": "Eğer devamını istiyorsan...", "delay": 1200},
                {"type": "incoming", "text": "Bana VIP olarak gel 👑💋", "delay": 1500},
            ],
        },
        {
            "name": "kiskanclik",
            "conversation": [
                {"type": "incoming", "text": "Sen kimle konuşuyordun az önce? 😤", "delay": 800},
                {"type": "pause", "delay": 2000},
                {"type": "outgoing", "text": "Ne? Kimseyle...", "delay": 1000},
                {"type": "pause", "delay": 1500},
                {"type": "incoming", "text": "Yalan söyleme bana.", "delay": 1200},
                {"type": "pause", "delay": 2000},
                {"type": "incoming", "text": "Online olduğunu gördüm ama bana yazmıyordun 😡", "delay": 1800},
                {"type": "pause", "delay": 2500},
                {"type": "outgoing", "text": "Kıskanıyor musun? 😏", "delay": 1000},
                {"type": "pause", "delay": 1500},
                {"type": "incoming", "text": "Evet kıskanıyorum. Problem?", "delay": 1000},
                {"type": "incoming", "text": "Sen BENİMSİN. Unutma. 🔥💋", "delay": 1500},
            ],
        },
        {
            "name": "sabah_uyanis",
            "conversation": [
                {"type": "incoming", "text": "Günaydın tatlım ☀️", "delay": 800},
                {"type": "pause", "delay": 2000},
                {"type": "incoming", "text": "Bu gece rüyamda seni gördüm...", "delay": 1500},
                {"type": "pause", "delay": 2000},
                {"type": "incoming", "text": "Ama söylemeye utanıyorum 😳", "delay": 1200},
                {"type": "pause", "delay": 2500},
                {"type": "outgoing", "text": "Söyle...", "delay": 800},
                {"type": "pause", "delay": 2000},
                {"type": "incoming", "text": "Hmm... yüz yüze anlatırım daha iyi 😏", "delay": 1500},
                {"type": "incoming", "text": "Ama önce kahvemi içeyim... sonra sana özel bir şey atarım 📸🔥", "delay": 2000},
            ],
        },
    ],
    "elif": [
        {
            "name": "itaat",
            "conversation": [
                {"type": "incoming", "text": "Neredesin?", "delay": 800},
                {"type": "pause", "delay": 2500},
                {"type": "incoming", "text": "Sana izin verdiğimi hatırlamıyorum. 😈", "delay": 1500},
                {"type": "pause", "delay": 2000},
                {"type": "outgoing", "text": "Özür dilerim...", "delay": 800},
                {"type": "pause", "delay": 1500},
                {"type": "incoming", "text": "Aferin. İyi çocuk.", "delay": 1000},
                {"type": "pause", "delay": 2500},
                {"type": "incoming", "text": "Şimdi bana ne yapacağını söyle.", "delay": 1500},
                {"type": "incoming", "text": "İtaat edersen... ödülünü alırsın 🖤⛓️", "delay": 2000},
            ],
        },
        {
            "name": "ceza",
            "conversation": [
                {"type": "incoming", "text": "Bugün sessizsin.", "delay": 800},
                {"type": "pause", "delay": 2000},
                {"type": "incoming", "text": "Bana yazmadan uyuduysan...", "delay": 1500},
                {"type": "pause", "delay": 2500},
                {"type": "incoming", "text": "Yarın çok pişman olacaksın. 😈", "delay": 1500},
                {"type": "pause", "delay": 2000},
                {"type": "outgoing", "text": "Ne yapacaksın? 😳", "delay": 1000},
                {"type": "pause", "delay": 2000},
                {"type": "incoming", "text": "Hmm... merak mı ediyorsun?", "delay": 1200},
                {"type": "incoming", "text": "Gel de gör. VIP'e yükselt kendini. 🔥⛓️", "delay": 2000},
            ],
        },
    ],
    "yuki": [
        {
            "name": "utangac_itiraf",
            "conversation": [
                {"type": "incoming", "text": "S-senpai... orada mısın? 🥺", "delay": 800},
                {"type": "pause", "delay": 2500},
                {"type": "outgoing", "text": "Buradayım Yuki 😊", "delay": 1000},
                {"type": "pause", "delay": 2000},
                {"type": "incoming", "text": "S-sana bir şey söylemek istiyorum ama...", "delay": 1500},
                {"type": "pause", "delay": 2000},
                {"type": "incoming", "text": "Çok utanıyorum >.<", "delay": 1000},
                {"type": "pause", "delay": 2500},
                {"type": "outgoing", "text": "Söyle bebek, utanma 💕", "delay": 1200},
                {"type": "pause", "delay": 2000},
                {"type": "incoming", "text": "B-bugün yatakta seni düşündüm... yüzüm çok kızardı 😳", "delay": 2000},
                {"type": "pause", "delay": 2500},
                {"type": "incoming", "text": "D-devamını duymak istersen... VIP ol senpai 🌸✨", "delay": 1800},
            ],
        },
        {
            "name": "cosplay",
            "conversation": [
                {"type": "incoming", "text": "Senpai! Bugün cosplay yaptım! ✨🌙", "delay": 800},
                {"type": "pause", "delay": 2000},
                {"type": "outgoing", "text": "Göster göster! 😍", "delay": 800},
                {"type": "pause", "delay": 1500},
                {"type": "incoming", "text": "A-ama çok açık oldu galiba... >///<", "delay": 1500},
                {"type": "pause", "delay": 2500},
                {"type": "incoming", "text": "Sence yakışmış mıydı?", "delay": 1200},
                {"type": "pause", "delay": 2000},
                {"type": "incoming", "text": "S-sadece sana gösterebilirim... VIP ol da atayım 🎀💕", "delay": 2000},
            ],
        },
    ],
    "defne": [
        {
            "name": "havuz",
            "conversation": [
                {"type": "incoming", "text": "Tatlım havuzdan yeni çıktım 💦", "delay": 800},
                {"type": "pause", "delay": 2000},
                {"type": "incoming", "text": "Daha bikinimle duruyorum...", "delay": 1500},
                {"type": "pause", "delay": 2500},
                {"type": "incoming", "text": "Görmek ister misin? 😏📸", "delay": 1200},
                {"type": "pause", "delay": 2000},
                {"type": "outgoing", "text": "Tabii ki! 🔥", "delay": 800},
                {"type": "pause", "delay": 2000},
                {"type": "incoming", "text": "Hmm ama bu özel koleksiyonumdan...", "delay": 1500},
                {"type": "incoming", "text": "VIP'ler görür sadece 💎👑 Bio'daki linke tıkla", "delay": 2000},
            ],
        },
        {
            "name": "alisveris",
            "conversation": [
                {"type": "incoming", "text": "Bebeğim bugün alışverişe çıktım 🛍️", "delay": 800},
                {"type": "pause", "delay": 2000},
                {"type": "incoming", "text": "Sence hangisi daha iyi? Siyah mı kırmızı mı? 😉", "delay": 1800},
                {"type": "pause", "delay": 2500},
                {"type": "outgoing", "text": "İkisi de 🔥", "delay": 800},
                {"type": "pause", "delay": 1500},
                {"type": "incoming", "text": "O zaman ikisini de deneyeyim sana 😈", "delay": 1500},
                {"type": "incoming", "text": "Mannequin challenge atacağım... VIP ol, kaçırma 💋", "delay": 2000},
            ],
        },
    ],
    "natasha": [
        {
            "name": "soguk_sicak",
            "conversation": [
                {"type": "incoming", "text": "Privyet.", "delay": 800},
                {"type": "pause", "delay": 3000},
                {"type": "outgoing", "text": "Selam Natasha 😊", "delay": 800},
                {"type": "pause", "delay": 2000},
                {"type": "incoming", "text": "Hmm. İlgimi çektiğini düşünme.", "delay": 1500},
                {"type": "pause", "delay": 2500},
                {"type": "incoming", "text": "...", "delay": 800},
                {"type": "pause", "delay": 2000},
                {"type": "incoming", "text": "Ama seninle farklı bir şey var. Nyet bilmiyorum neden.", "delay": 2000},
                {"type": "pause", "delay": 2500},
                {"type": "incoming", "text": "Bu gece vodka içiyorum yalnız... gel konuşalım 🥃❄️", "delay": 2000},
            ],
        },
    ],
    "selin": [
        {
            "name": "ofis_gizli",
            "conversation": [
                {"type": "incoming", "text": "Patron toplantıda... sana yazıyorum 👓🔥", "delay": 800},
                {"type": "pause", "delay": 2000},
                {"type": "incoming", "text": "Gözlüğümü çıkarınca bambaşka biriyim, biliyorsun...", "delay": 1800},
                {"type": "pause", "delay": 2500},
                {"type": "outgoing", "text": "Gece Selin'i özledim 😈", "delay": 1000},
                {"type": "pause", "delay": 2000},
                {"type": "incoming", "text": "Akşam aktif olurum...", "delay": 1200},
                {"type": "incoming", "text": "Ama VIP'ler özel muamele alır 😉🖤", "delay": 2000},
            ],
        },
    ],
    "aylin": [
        {
            "name": "ogretmen_dersi",
            "conversation": [
                {"type": "incoming", "text": "Delikanlım, bugün ders bitmedi 🍒", "delay": 800},
                {"type": "pause", "delay": 2000},
                {"type": "incoming", "text": "Sana özel bir ders vermek istiyorum...", "delay": 1500},
                {"type": "pause", "delay": 2500},
                {"type": "outgoing", "text": "Ne dersi hocam? 😏", "delay": 1000},
                {"type": "pause", "delay": 2000},
                {"type": "incoming", "text": "Unutamayacağın türden... 😈", "delay": 1200},
                {"type": "incoming", "text": "Ama bu ders sadece VIP öğrencilere özel 🍷🔥", "delay": 2000},
            ],
        },
    ],
    "zeynep": [
        {
            "name": "yurt_yalniz",
            "conversation": [
                {"type": "incoming", "text": "Oda arkadaşım çıktı, yalnızım... 🎀", "delay": 800},
                {"type": "pause", "delay": 2000},
                {"type": "incoming", "text": "Ders çok sıktı bugün, seninle konuşmak daha eğlenceli!", "delay": 1800},
                {"type": "pause", "delay": 2500},
                {"type": "outgoing", "text": "Ne yapıyorsun şimdi? 😏", "delay": 1000},
                {"type": "pause", "delay": 2000},
                {"type": "incoming", "text": "Yatakta uzanıyorum... ilk defa böyle konuşuyorum biriyle 😳", "delay": 2000},
                {"type": "pause", "delay": 2500},
                {"type": "incoming", "text": "Sana bir isteğim var ama... utanıyorum sormaya 🙈", "delay": 1800},
                {"type": "incoming", "text": "VIP ol da söyleyeyim... 💕", "delay": 1500},
            ],
        },
    ],
}


# ============================================================
# KARAKTER TAGLINE'LARI & CAPTION'LARI
# ============================================================

CHARACTER_TAGLINES = {
    "mia": {
        "tagline": "Gündüzleri masum... Geceleri sınır tanımaz.",
        "short_tagline": "Masum ama tehlikeli 🌸",
        "captions": [
            "02:14'te gelen mesaj... 🌙💋 Devamı bio'da",
            "Uyumadan önce bir mesaj geldi... açar mısın? 🔥",
            "Mia seni bekliyor. Sen onu bekletme. 🌸",
            "Bu gece farklı... bu gece Mia'nın gecesi 💋🔥",
        ],
    },
    "elif": {
        "tagline": "İtaat et. Ödülünü al.",
        "short_tagline": "Sahiben konuşuyor 🔥",
        "captions": [
            "Elif'e karşı gelinmez. İtaat edersen ödül var 😈⛓️",
            "Cesaretin varsa gel. Yoksa Elif sana gelir. 🖤",
            "Bu kadın emir verir, sen dinlersin. 🔥",
            "Elif'in kuralları var. İlki: SEN BENİMSİN.",
        ],
    },
    "yuki": {
        "tagline": "Utangaç görünür ama... sadece sana özel.",
        "short_tagline": "K-kalbim çarpıyor >.<",
        "captions": [
            "S-senpai bu mesajı okuyorsan... gel konuşalım 🥺✨",
            "Yuki bugün cesur. Belki. Biraz. >///<",
            "Utangaç ama... sana her şeyi anlatır 🌸💕",
            "Bu kawaii kızın gizli bir tarafı var 🌙",
        ],
    },
    "defne": {
        "tagline": "Lüks, pahalı ve kışkırtıcı.",
        "short_tagline": "VIP hayat, VIP kız 💎",
        "captions": [
            "Defne'nin dünyasına giriş ücretsiz değil 💎👑",
            "Bu güzelliğe yetebilecek misin? 💋🔥",
            "Dubai'den sevgilerle... Defne 💎",
            "Pahalı zevkler, pahalı kadın. Ama değer 👑",
        ],
    },
    "natasha": {
        "tagline": "Soğuk güzellik, ateşli tutkular.",
        "short_tagline": "Cold outside, fire inside ❄️🔥",
        "captions": [
            "Privyet... Bu Rus güzele yaklaşmaya cesaretin var mı? ❄️",
            "Soğuk bakışların ardında ateş var 🔥",
            "Natasha seçer, sen seçilirsin. ❄️💋",
            "Moskova'nın soğuğu, İstanbul'un ateşi 🥃",
        ],
    },
    "selin": {
        "tagline": "Gündüz sekreter, gece yırtıcı.",
        "short_tagline": "Gözlüğü çıkarınca... 👓🔥",
        "captions": [
            "09:00 - Sekreter Selin 👓 | 22:00 - ??? 🔥",
            "Gözlüğünü çıkardığında tanıyamazsın 😈",
            "Patron bilmiyor. Ama sen bileceksin. 🖤",
            "Çift kişilikli, tek tutkulu. Selin. 👓🔥",
        ],
    },
    "aylin": {
        "tagline": "Tecrübe, tutku, sınırsızlık.",
        "short_tagline": "En iyi dersler ondan 🍒",
        "captions": [
            "Aylin hoca bugün özel ders veriyor 🍒🔥",
            "35 yaşın verdiği özgüven... ve tutku 🍷",
            "Tecrübeli kadın ne istediğini bilir 😈",
            "Bu ders unutulmaz olacak... 🍒",
        ],
    },
    "zeynep": {
        "tagline": "Masum ama keşfetmeye istekli.",
        "short_tagline": "İlk defa böyle hissediyorum 🎀",
        "captions": [
            "Zeynep ilk defa cesaret etti... 🎀😳",
            "Üniversiteli, masum, meraklı... ve yalnız 🙈",
            "İlk adımı o atıyor. Sen karşılık ver. 💕",
            "Yurt odası, yalnızlık, merak... 🎀🔥",
        ],
    },
}


# ============================================================
# HASHTAG SETLERI
# ============================================================

HASHTAG_SETS = {
    "base": [
        "#aicompanion", "#telegrambot", "#aichat", "#virtualcompanion",
        "#yapayzekapartner", "#dijitalsevgili", "#chatbot",
    ],
    "turkish": [
        "#türkiye", "#istanbul", "#gece", "#yalnızlık",
        "#sohbet", "#flört", "#aşk", "#telegram",
    ],
    "character_specific": {
        "mia": ["#sweetgirl", "#masum", "#gece", "#tatli"],
        "elif": ["#dominant", "#bosslady", "#powerwoman", "#itaat"],
        "yuki": ["#kawaii", "#anime", "#cosplay", "#senpai", "#cute"],
        "defne": ["#luxury", "#vip", "#model", "#influencer", "#glamour"],
        "natasha": ["#russianbeauty", "#exotic", "#model", "#coldbeauty"],
        "selin": ["#secretary", "#officelife", "#doublelfe", "#transformation"],
        "aylin": ["#mature", "#experienced", "#teacher", "#confident"],
        "zeynep": ["#university", "#innocent", "#curious", "#student"],
    },
}


def get_hashtags(character_id: str, limit: int = 15) -> str:
    """Karakter icin hashtag seti dondurur."""
    tags = []
    tags.extend(HASHTAG_SETS["base"][:4])
    tags.extend(HASHTAG_SETS["turkish"][:4])
    char_tags = HASHTAG_SETS["character_specific"].get(character_id, [])
    tags.extend(char_tags)
    return " ".join(tags[:limit])


def get_random_scenario(character_id: str) -> dict:
    """Karakter icin rastgele bir sohbet senaryosu dondurur."""
    import random
    scenarios = CHAT_SCENARIOS.get(character_id, CHAT_SCENARIOS["mia"])
    return random.choice(scenarios)


def get_random_caption(character_id: str) -> str:
    """Karakter icin rastgele bir caption dondurur."""
    import random
    info = CHARACTER_TAGLINES.get(character_id, CHARACTER_TAGLINES["mia"])
    return random.choice(info["captions"])


def get_all_characters() -> list:
    """Tum karakter ID'lerini dondurur."""
    return list(CHAT_SCENARIOS.keys())
