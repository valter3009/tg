"""
Переводы описаний ветра и советов по одежде для бота GidMeteo
"""

import random

# Описания ветра на разных языках
WIND_DESCRIPTIONS = {
    'ru': {
        'dead_calm': {
            'name': 'Мертвый штиль',
            'range': '0–0,2 м/с',
            'descriptions': [
                "Воздух настолько неподвижен, что даже молекулы кислорода подали заявление на пособие по безработице.",
                "Атмосфера замерла в ожидании, как будто природа нажала кнопку паузы и пошла за кофе.",
                "Воздушные массы устроили забастовку — видимо, требуют улучшения условий труда.",
                "Полное безветрие: даже флюгеры легли спать от скуки."
            ]
        },
        'ghostly_breath': {
            'name': 'Призрачное дуновение',
            'range': '0,3–1,5 м/с',
            'descriptions': [
                "Такой слабый ветерок, что пыль просто меняет адрес, не покидая вашего района.",
                "Воздух шевелится так нежно, что бабочки используют его как спа-процедуру.",
                "Ветер работает удаленно — формально присутствует, но никто не замечает результатов.",
                "Еле различимое движение воздуха, которое могли бы почувствовать только особо чувствительные паутины."
            ]
        },
        'lazy_breeze': {
            'name': 'Ленивый бриз',
            'range': '1,6–3,3 м/с',
            'descriptions': [
                "Ветер с амбициями офисного планктона — вроде работает, но никаких реальных результатов.",
                "Воздушный поток на минималках: можно было бы не напрягаться, но для приличия шевелится.",
                "Ветер в режиме энергосбережения — двигается ровно настолько, чтобы не уволили.",
                "Бриз-интроверт: присутствует, но старается никого не беспокоить."
            ]
        },
        'timid_gust': {
            'name': 'Робкий порыв',
            'range': '3,4–5,4 м/с',
            'descriptions': [
                "Достаточно сильный, чтобы украсть ваш лотерейный билет, но недостаточно наглый, чтобы унести вашу шляпу.",
                "Ветер с характером подростка — пытается казаться крутым, но пока только раздражает.",
                "Воздушные массы флиртуют с вашей одеждой, но до серьезных отношений дело не доходит.",
                "Порывы с претензией на значимость, но на деле — просто шумные пустышки."
            ]
        },
        'active_onlooker': {
            'name': 'Активный зевака',
            'range': '5,5–7,9 м/с',
            'descriptions': [
                "Превращает ваш тщательно уложенный образ в пугало, но хотя бы бесплатно выгуливает мусор с вашего двора.",
                "Ветер решил, что ваша прическа слишком скучная, и внес творческие коррективы без вашего согласия.",
                "Воздушный поток с манерами хулигана: толкается, но извиняться не собирается.",
                "Достаточно силен, чтобы испортить селфи, но слишком слаб для страховых выплат."
            ]
        },
        'persistent_pusher': {
            'name': 'Настырный толкач',
            'range': '8,0–10,7 м/с',
            'descriptions': [
                "Ваша прическа теперь напоминает абстрактное искусство, за которое какой-нибудь богач заплатил бы миллионы.",
                "Ветер работает стилистом-самоучкой: результат спорный, но уверенность в себе зашкаливает.",
                "Воздушные массы устроили ревизию вашего гардероба прямо на вас — и им не нравится то, что они нашли.",
                "Идеальная сила для бесплатной аэродинамической терапии — вас буквально выдувает из зоны комфорта."
            ]
        },
        'aggressive_debater': {
            'name': 'Агрессивный спорщик',
            'range': '10,8–13,8 м/с',
            'descriptions': [
                "Ветер с дипломом адвоката — спорит с каждым встречным и обычно выигрывает процесс.",
                "Воздушный поток с агрессивной позицией по всем вопросам, включая ваше право идти прямо.",
                "Ветер ведет себя как коллектор: настойчив, грубоват и не принимает 'нет' в качестве ответа.",
                "Атмосферное давление решило показать, кто тут главный, и ваш зонт с этим категорически не согласен."
            ]
        },
        'unstoppable_hooligan': {
            'name': 'Неудержимый хулиган',
            'range': '13,9–17,1 м/с',
            'descriptions': [
                "Превращает обычную прогулку в непреднамеренный кастинг на роль Мэри Поппинс.",
                "Ветер с амбициями циклона, но пока только тренируется на вас и ближайших мусорных баках.",
                "Воздушные массы перешли на личности и вашу личную территорию одновременно.",
                "Природа устроила краш-тест вашей устойчивости — и, судя по всему, вы его не прошли."
            ]
        },
        'merciless_terrorist': {
            'name': 'Беспощадный террорист',
            'range': '17,2–20,7 м/с',
            'descriptions': [
                "Деревья кланяются так низко, что практически выдергивают собственные корни в знак подчинения новому воздушному диктатору.",
                "Ветер перешел в режим тоталитаризма: все, что не прикручено, теперь собственность атмосферы.",
                "Воздушные массы объявили вас и всё вокруг временно реквизированным имуществом матушки-природы.",
                "Это уже не ветер — это воздушный переворот с попыткой свержения законов гравитации."
            ]
        },
        'apocalyptic_destroyer': {
            'name': 'Апокалиптический разрушитель',
            'range': '>20,8 м/с',
            'descriptions': [
                "Момент, когда вы понимаете, что ипотека больше не ваша проблема, поскольку дом теперь существует в альтернативном измерении.",
                "Ветер решил устроить бесплатный редизайн ландшафта — без вашего согласия и участия проектировщиков.",
                "Апокалипсис начинается именно так: с ветра, которому надоело быть просто погодным явлением.",
                "Воздушные массы сошли с ума и объявили войну всему, что имеет физическую форму, включая вашу крышу."
            ]
        },
    },
    'en': {
        'dead_calm': {
            'name': 'Dead Calm',
            'range': '0–0.2 m/s',
            'descriptions': [
                "The air is so motionless that even oxygen molecules have filed for unemployment benefits.",
                "The atmosphere froze in anticipation, as if nature pressed the pause button and went for coffee.",
                "Air masses went on strike — apparently demanding better working conditions.",
                "Complete windlessness: even weathervanes fell asleep from boredom."
            ]
        },
        'ghostly_breath': {
            'name': 'Ghostly Breath',
            'range': '0.3–1.5 m/s',
            'descriptions': [
                "Such a weak breeze that dust just changes addresses without leaving your neighborhood.",
                "The air moves so gently that butterflies use it as a spa treatment.",
                "Wind works remotely — formally present, but no one notices the results.",
                "A barely perceptible air movement that only particularly sensitive spider webs could feel."
            ]
        },
        'lazy_breeze': {
            'name': 'Lazy Breeze',
            'range': '1.6–3.3 m/s',
            'descriptions': [
                "Wind with the ambitions of office plankton — seems to work, but no real results.",
                "Airflow on minimal settings: could not bother, but moves for decency's sake.",
                "Wind in energy saving mode — moves just enough not to get fired.",
                "Introvert breeze: present, but tries not to disturb anyone."
            ]
        },
        'timid_gust': {
            'name': 'Timid Gust',
            'range': '3.4–5.4 m/s',
            'descriptions': [
                "Strong enough to steal your lottery ticket, but not bold enough to take your hat.",
                "Wind with the character of a teenager — tries to seem cool, but only annoys so far.",
                "Air masses flirt with your clothes, but it doesn't come to serious relationships.",
                "Gusts with a claim to significance, but in fact — just noisy dummies."
            ]
        },
        'active_onlooker': {
            'name': 'Active Onlooker',
            'range': '5.5–7.9 m/s',
            'descriptions': [
                "Turns your carefully styled look into a scarecrow, but at least walks your yard trash for free.",
                "Wind decided that your hairstyle is too boring and made creative corrections without your consent.",
                "Airflow with hooligan manners: pushes, but doesn't intend to apologize.",
                "Strong enough to ruin a selfie, but too weak for insurance claims."
            ]
        },
        'persistent_pusher': {
            'name': 'Persistent Pusher',
            'range': '8.0–10.7 m/s',
            'descriptions': [
                "Your hairstyle now resembles abstract art that some rich person would pay millions for.",
                "Wind works as a self-taught stylist: the result is controversial, but self-confidence is off the charts.",
                "Air masses audited your wardrobe right on you — and they don't like what they found.",
                "Perfect force for free aerodynamic therapy — you are literally blown out of your comfort zone."
            ]
        },
        'aggressive_debater': {
            'name': 'Aggressive Debater',
            'range': '10.8–13.8 m/s',
            'descriptions': [
                "Wind with a law degree — argues with everyone it meets and usually wins the case.",
                "Airflow with an aggressive position on all issues, including your right to walk straight.",
                "Wind behaves like a debt collector: persistent, rude, and doesn't take 'no' for an answer.",
                "Atmospheric pressure decided to show who's boss, and your umbrella categorically disagrees."
            ]
        },
        'unstoppable_hooligan': {
            'name': 'Unstoppable Hooligan',
            'range': '13.9–17.1 m/s',
            'descriptions': [
                "Turns a regular walk into an unintentional audition for the role of Mary Poppins.",
                "Wind with cyclone ambitions, but for now only practices on you and nearby garbage cans.",
                "Air masses got personal and invaded your personal space simultaneously.",
                "Nature crash-tested your stability — and apparently, you failed it."
            ]
        },
        'merciless_terrorist': {
            'name': 'Merciless Terrorist',
            'range': '17.2–20.7 m/s',
            'descriptions': [
                "Trees bow so low they almost pull out their own roots in submission to the new air dictator.",
                "Wind switched to totalitarian mode: everything not bolted down is now property of the atmosphere.",
                "Air masses declared you and everything around temporarily requisitioned property of Mother Nature.",
                "This is no longer wind — it's an aerial coup attempting to overthrow the laws of gravity."
            ]
        },
        'apocalyptic_destroyer': {
            'name': 'Apocalyptic Destroyer',
            'range': '>20.8 m/s',
            'descriptions': [
                "The moment you realize your mortgage is no longer your problem, as your house now exists in an alternate dimension.",
                "Wind decided to do a free landscape redesign — without your consent and without designers.",
                "The apocalypse starts exactly like this: with wind that got tired of being just a weather phenomenon.",
                "Air masses went crazy and declared war on everything with physical form, including your roof."
            ]
        },
    },
    'es': {
        'dead_calm': {
            'name': 'Calma Total',
            'range': '0–0,2 m/s',
            'descriptions': [
                "El aire está tan inmóvil que incluso las moléculas de oxígeno han solicitado el subsidio de desempleo.",
                "La atmósfera se congeló en anticipación, como si la naturaleza hubiera presionado el botón de pausa y fuera por café.",
                "Las masas de aire se declararon en huelga, aparentemente exigiendo mejores condiciones laborales.",
                "Ausencia total de viento: incluso las veletas se durmieron de aburrimiento."
            ]
        },
        'ghostly_breath': {
            'name': 'Aliento Fantasmal',
            'range': '0,3–1,5 m/s',
            'descriptions': [
                "Una brisa tan débil que el polvo simplemente cambia de dirección sin salir de tu vecindario.",
                "El aire se mueve tan suavemente que las mariposas lo usan como tratamiento de spa.",
                "El viento trabaja de forma remota: formalmente presente, pero nadie nota los resultados.",
                "Un movimiento de aire apenas perceptible que solo las telarañas particularmente sensibles podrían sentir."
            ]
        },
        'lazy_breeze': {
            'name': 'Brisa Perezosa',
            'range': '1,6–3,3 m/s',
            'descriptions': [
                "Viento con las ambiciones del plancton de oficina: parece trabajar, pero sin resultados reales.",
                "Flujo de aire al mínimo: podría no molestarse, pero se mueve por decencia.",
                "Viento en modo de ahorro de energía: se mueve lo justo para no ser despedido.",
                "Brisa introvertida: presente, pero intenta no molestar a nadie."
            ]
        },
        'timid_gust': {
            'name': 'Ráfaga Tímida',
            'range': '3,4–5,4 m/s',
            'descriptions': [
                "Suficientemente fuerte para robar tu boleto de lotería, pero no lo bastante atrevido para llevarse tu sombrero.",
                "Viento con carácter de adolescente: intenta parecer genial, pero por ahora solo molesta.",
                "Las masas de aire coquetean con tu ropa, pero no llega a relaciones serias.",
                "Ráfagas con pretensiones de importancia, pero en realidad, solo ruido vacío."
            ]
        },
        'active_onlooker': {
            'name': 'Mirón Activo',
            'range': '5,5–7,9 m/s',
            'descriptions': [
                "Convierte tu imagen cuidadosamente arreglada en un espantapájaros, pero al menos pasea gratis la basura de tu patio.",
                "El viento decidió que tu peinado era demasiado aburrido e hizo correcciones creativas sin tu consentimiento.",
                "Flujo de aire con modales de gamberro: empuja, pero no piensa disculparse.",
                "Suficientemente fuerte para arruinar un selfie, pero demasiado débil para reclamos de seguro."
            ]
        },
        'persistent_pusher': {
            'name': 'Empujón Persistente',
            'range': '8,0–10,7 m/s',
            'descriptions': [
                "Tu peinado ahora se parece al arte abstracto por el que algún rico pagaría millones.",
                "El viento trabaja como estilista autodidacta: el resultado es controvertido, pero la confianza en sí mismo está por las nubes.",
                "Las masas de aire auditaron tu guardarropa directamente sobre ti, y no les gusta lo que encontraron.",
                "Fuerza perfecta para terapia aerodinámica gratuita: literalmente te saca de tu zona de confort."
            ]
        },
        'aggressive_debater': {
            'name': 'Debatiente Agresivo',
            'range': '10,8–13,8 m/s',
            'descriptions': [
                "Viento con título de abogado: discute con todos los que encuentra y suele ganar el caso.",
                "Flujo de aire con posición agresiva en todos los temas, incluido tu derecho a caminar recto.",
                "El viento se comporta como un cobrador de deudas: persistente, grosero y no acepta 'no' como respuesta.",
                "La presión atmosférica decidió mostrar quién manda, y tu paraguas está categóricamente en desacuerdo."
            ]
        },
        'unstoppable_hooligan': {
            'name': 'Gamberro Imparable',
            'range': '13,9–17,1 m/s',
            'descriptions': [
                "Convierte un paseo normal en una audición no intencionada para el papel de Mary Poppins.",
                "Viento con ambiciones de ciclón, pero por ahora solo practica contigo y los contenedores de basura cercanos.",
                "Las masas de aire se pusieron personales e invadieron tu espacio personal simultáneamente.",
                "La naturaleza hizo una prueba de choque de tu estabilidad, y aparentemente, la fallaste."
            ]
        },
        'merciless_terrorist': {
            'name': 'Terrorista Despiadado',
            'range': '17,2–20,7 m/s',
            'descriptions': [
                "Los árboles se inclinan tan bajo que casi arrancan sus propias raíces en sumisión al nuevo dictador aéreo.",
                "El viento cambió a modo totalitario: todo lo que no esté atornillado ahora es propiedad de la atmósfera.",
                "Las masas de aire te declararon a ti y a todo lo que te rodea propiedad temporalmente requisada de la Madre Naturaleza.",
                "Esto ya no es viento: es un golpe aéreo que intenta derrocar las leyes de la gravedad."
            ]
        },
        'apocalyptic_destroyer': {
            'name': 'Destructor Apocalíptico',
            'range': '>20,8 m/s',
            'descriptions': [
                "El momento en que te das cuenta de que tu hipoteca ya no es tu problema, ya que tu casa ahora existe en una dimensión alternativa.",
                "El viento decidió hacer un rediseño gratuito del paisaje, sin tu consentimiento y sin diseñadores.",
                "El apocalipsis comienza exactamente así: con viento que se cansó de ser solo un fenómeno meteorológico.",
                "Las masas de aire se volvieron locas y declararon la guerra a todo lo que tiene forma física, incluido tu techo."
            ]
        },
    },
    'de': {
        'dead_calm': {
            'name': 'Totale Windstille',
            'range': '0–0,2 m/s',
            'descriptions': [
                "Die Luft ist so regungslos, dass sogar Sauerstoffmoleküle Arbeitslosengeld beantragt haben.",
                "Die Atmosphäre erstarrte in Erwartung, als hätte die Natur die Pausentaste gedrückt und wäre Kaffee holen gegangen.",
                "Luftmassen streikten — offenbar fordern sie bessere Arbeitsbedingungen.",
                "Völlige Windstille: Sogar Wetterfahnen sind vor Langeweile eingeschlafen."
            ]
        },
        'ghostly_breath': {
            'name': 'Gespenstischer Hauch',
            'range': '0,3–1,5 m/s',
            'descriptions': [
                "So eine schwache Brise, dass Staub einfach die Adresse wechselt, ohne deine Nachbarschaft zu verlassen.",
                "Die Luft bewegt sich so sanft, dass Schmetterlinge sie als Spa-Behandlung nutzen.",
                "Wind arbeitet remote — formal anwesend, aber niemand bemerkt die Ergebnisse.",
                "Eine kaum wahrnehmbare Luftbewegung, die nur besonders empfindliche Spinnennetze spüren könnten."
            ]
        },
        'lazy_breeze': {
            'name': 'Faule Brise',
            'range': '1,6–3,3 m/s',
            'descriptions': [
                "Wind mit den Ambitionen von Büro-Plankton — scheint zu arbeiten, aber keine echten Ergebnisse.",
                "Luftstrom auf Minimaleinstellungen: könnte sich nicht bemühen, bewegt sich aber aus Anstand.",
                "Wind im Energiesparmodus — bewegt sich gerade genug, um nicht gefeuert zu werden.",
                "Introvertierte Brise: anwesend, versucht aber niemanden zu stören."
            ]
        },
        'timid_gust': {
            'name': 'Schüchterne Böe',
            'range': '3,4–5,4 m/s',
            'descriptions': [
                "Stark genug, um dein Lotterielos zu stehlen, aber nicht mutig genug, um deinen Hut zu nehmen.",
                "Wind mit dem Charakter eines Teenagers — versucht cool zu wirken, nervt aber bisher nur.",
                "Luftmassen flirten mit deiner Kleidung, aber zu ernsten Beziehungen kommt es nicht.",
                "Böen mit Anspruch auf Bedeutung, aber tatsächlich — nur laute Attrappen."
            ]
        },
        'active_onlooker': {
            'name': 'Aktiver Gaffer',
            'range': '5,5–7,9 m/s',
            'descriptions': [
                "Verwandelt dein sorgfältig gestyltes Aussehen in eine Vogelscheuche, führt aber wenigstens kostenlos deinen Hofmüll aus.",
                "Wind entschied, dass deine Frisur zu langweilig ist und machte kreative Korrekturen ohne deine Zustimmung.",
                "Luftstrom mit Hooligan-Manieren: schubst, denkt aber nicht daran, sich zu entschuldigen.",
                "Stark genug, um ein Selfie zu ruinieren, aber zu schwach für Versicherungsansprüche."
            ]
        },
        'persistent_pusher': {
            'name': 'Hartnäckiger Schubser',
            'range': '8,0–10,7 m/s',
            'descriptions': [
                "Deine Frisur erinnert jetzt an abstrakte Kunst, für die irgendein Reicher Millionen zahlen würde.",
                "Wind arbeitet als autodidaktischer Stylist: Das Ergebnis ist umstritten, aber das Selbstvertrauen ist durch die Decke.",
                "Luftmassen prüften deine Garderobe direkt an dir — und ihnen gefällt nicht, was sie fanden.",
                "Perfekte Kraft für kostenlose aerodynamische Therapie — du wirst buchstäblich aus deiner Komfortzone geblasen."
            ]
        },
        'aggressive_debater': {
            'name': 'Aggressiver Debattierer',
            'range': '10,8–13,8 m/s',
            'descriptions': [
                "Wind mit Anwaltsabschluss — streitet mit jedem, dem er begegnet, und gewinnt normalerweise den Fall.",
                "Luftstrom mit aggressiver Position zu allen Fragen, einschließlich deines Rechts, geradeaus zu gehen.",
                "Wind verhält sich wie ein Inkassobüro: hartnäckig, grob und akzeptiert 'nein' nicht als Antwort.",
                "Atmosphärischer Druck beschloss zu zeigen, wer der Boss ist, und dein Regenschirm ist kategorisch anderer Meinung."
            ]
        },
        'unstoppable_hooligan': {
            'name': 'Unaufhaltsamer Rowdy',
            'range': '13,9–17,1 m/s',
            'descriptions': [
                "Verwandelt einen normalen Spaziergang in ein unbeabsichtigtes Vorsprechen für die Rolle von Mary Poppins.",
                "Wind mit Zyklon-Ambitionen, übt aber vorerst nur an dir und nahen Mülltonnen.",
                "Luftmassen wurden persönlich und drangen gleichzeitig in deinen persönlichen Raum ein.",
                "Die Natur führte einen Crashtest deiner Stabilität durch — und offenbar hast du ihn nicht bestanden."
            ]
        },
        'merciless_terrorist': {
            'name': 'Gnadenloser Terrorist',
            'range': '17,2–20,7 m/s',
            'descriptions': [
                "Bäume verneigen sich so tief, dass sie fast ihre eigenen Wurzeln herausreißen in Unterwerfung vor dem neuen Luftdiktator.",
                "Wind wechselte in den totalitären Modus: Alles, was nicht festgeschraubt ist, ist jetzt Eigentum der Atmosphäre.",
                "Luftmassen erklärten dich und alles um dich herum zu vorübergehend beschlagnahmtem Eigentum von Mutter Natur.",
                "Das ist kein Wind mehr — das ist ein Luftputsch, der versucht, die Gesetze der Schwerkraft zu stürzen."
            ]
        },
        'apocalyptic_destroyer': {
            'name': 'Apokalyptischer Zerstörer',
            'range': '>20,8 m/s',
            'descriptions': [
                "Der Moment, in dem du erkennst, dass deine Hypothek nicht mehr dein Problem ist, da dein Haus jetzt in einer alternativen Dimension existiert.",
                "Wind beschloss, eine kostenlose Landschaftsneugestaltung durchzuführen — ohne deine Zustimmung und ohne Designer.",
                "Die Apokalypse beginnt genau so: mit Wind, der es satt hat, nur ein Wetterphänomen zu sein.",
                "Luftmassen sind verrückt geworden und haben allem mit physischer Form den Krieg erklärt, einschließlich deines Dachs."
            ]
        },
    },
}

def get_wind_category(wind_speed):
    """Определяет категорию ветра по скорости"""
    if wind_speed <= 0.2:
        return 'dead_calm'
    elif wind_speed <= 1.5:
        return 'ghostly_breath'
    elif wind_speed <= 3.3:
        return 'lazy_breeze'
    elif wind_speed <= 5.4:
        return 'timid_gust'
    elif wind_speed <= 7.9:
        return 'active_onlooker'
    elif wind_speed <= 10.7:
        return 'persistent_pusher'
    elif wind_speed <= 13.8:
        return 'aggressive_debater'
    elif wind_speed <= 17.1:
        return 'unstoppable_hooligan'
    elif wind_speed <= 20.7:
        return 'merciless_terrorist'
    else:
        return 'apocalyptic_destroyer'

def get_wind_description(wind_speed, language='ru'):
    """
    Возвращает описание ветра в зависимости от его скорости и языка

    Args:
        wind_speed (float): Скорость ветра в м/с
        language (str): Код языка ('ru', 'en', 'es', 'de')

    Returns:
        tuple: (название ветра, диапазон скорости, описание)
    """
    if language not in WIND_DESCRIPTIONS:
        language = 'ru'

    category = get_wind_category(wind_speed)
    wind_data = WIND_DESCRIPTIONS[language][category]

    return (
        wind_data['name'],
        wind_data['range'],
        random.choice(wind_data['descriptions'])
    )

# Префикс для советов по одежде
CLOTHING_ADVICE_PREFIX = {
    'ru': 'Ветер:',
    'en': 'Wind:',
    'es': 'Viento:',
    'de': 'Wind:',
}
