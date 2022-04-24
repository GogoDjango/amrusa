from aiohttp import web
import aiohttp_cors

HOST_IP = 'localhost'
HOST_PORT = '8000'
curr_question = 0
quiz = {'Разработка игр': False,
        'Java-разработка': False,
        'Backend-разработка': False,
        'Frontend-разработка': False,
        'Разработка чат-ботов и голосовых ассистентов': False,
        'PHP-разработка': False,
        'Мобильная разработка': False,
        'Разработка мини-приложений': False}


def send_ans(req, text1, end=True, ssml=False):
    if not ssml:
        response = {"version": req["version"], "session": req["session"],
                    "response": {"end_session": end}}
        response["response"]["text"] = text1
        return response


def send_xml(req, output, speech, end=True):
    response = {"version": req["version"], "session": req["session"],
                "response": {"end_session": end}}
    response["response"]["text"] = output
    print(output, speech)
    command = f'<?xml version =\"1.0\" encoding=\"UTF-8\"?><speak version=\"1.1\" xmlns:mailru=\"[http://vc.go.mail.ru]\" lang=\"ru\">'
    command += speech + '</speak>'
    response["response"]["tts_type"] = "ssml"
    response["response"]["ssml"] = command
    return response


def send_img(req):
    response = {"version": req["version"], "session": req["session"], "response": {
        "text": "Да, все. В довесок держи Бабулеха",
        "tts": "Да, все. В довесок держи ^Бабул`еха^",
        "card": {
            "type": "BigImage",
            "image_id": 457239017
        },
        "end_session": False
    }}
    return response


def send_app(req, app):
    response = {"version": req["version"],
                "session": {'session_id': req["session"]['session_id'], 'message_id': req["session"]['message_id'],
                            'user_id': req["session"]['user_id']}, "response": {
            "text": 'Чуть не забыла! Зови друзей в Вездекод.',
            "tts": "Чуть не забыла! Зови друзей в Вездекод.",
            "card": {
                "type": "MiniApp",
                "url": ["https://vk.com/taxi"]
            },
            "end_session": True
        }}
    return response


async def webhook(request_obj):
    request = await request_obj.json()
    message = request['request']['original_utterance'].lower()
    print(message, request['session']['message_id'])
    if message in ['вездекод', 'вездеход']:
        response = send_ans(request,
                            'Привет Везде`кодерам! Давайте пройдем ^опр`ос^! Вопрос №1. Вам ^нравится^ разработка игр?<speaker audio=marusia-sounds/things-cuckoo-clock-2>',
                            end=False)
    elif message in ['да', 'нет']:
        match request['session']['message_id']:
            case 1:
                quiz['Разработка игр'] = True if message == 'да' else False
                response = send_ans(request,
                                    'Вопрос №2. Вам ^нравится^ разрабатывать API-с`ервисы?<speaker audio=marusia-sounds/things-cuckoo-clock-2>',
                                    end=False)
            case 2:
                quiz['Backend-разработка'] = True if message == 'да' else False
                response = send_ans(request,
                                    'Вопрос №3. Вам ^нравится^ разрабатывать приложения на Java?<speaker audio=marusia-sounds/things-cuckoo-clock-2>',
                                    end=False)
            case 3:
                quiz['Java-разработка'] = True if message == 'да' else False
                response = send_ans(request,
                                    'Вопрос №4. Вам ^нравится^ разрабатывать чат-ботов?<speaker audio=marusia-sounds/things-cuckoo-clock-2>',
                                    end=False)
            case 4:
                quiz['Разработка чат-ботов и голосовых ассистентов'] = True if message == 'да' else False
                response = send_ans(request,
                                    'Вопрос №5. Вам ^нравится^ работать с голосовыми ассистентами?<speaker audio=marusia-sounds/things-cuckoo-clock-2>',
                                    end=False)
            case 5:
                quiz['Разработка чат-ботов и голосовых ассистентов'] = True if message == 'да' else quiz[
                    'Разработка чат-ботов и голосовых ассистентов']
                response = send_ans(request,
                                    'Вопрос №6. Вам ^нравится^ разрабатывать на PHP?<speaker audio=marusia-sounds/things-cuckoo-clock-2>',
                                    end=False)
            case 6:
                quiz['PHP-разработка'] = True if message == 'да' else False
                response = send_ans(request,
                                    'Вопрос №7. Вам ^нравится^ разрабатывать мобильные приложения?<speaker audio=marusia-sounds/things-cuckoo-clock-2>',
                                    end=False)
            case 7:
                quiz['Мобильная разработка'] = True if message == 'да' else False
                response = send_ans(request,
                                    'Вопрос №8. Вам ^нравится^ разрабатывать мини-приложения?<speaker audio=marusia-sounds/things-cuckoo-clock-2>',
                                    end=False)
            case 8:
                quiz['Разработка мини-приложений'] = True if message == 'да' else False
                buff = ''
                for category in [key for key in quiz if quiz[key] == True]:
                    buff += category + '{,}{-}'
                buff = buff[:-6]
                output = f'Подсчитываю результаты...\n^Вот^ чем вам понравится заниматься:\n{buff}'
                speech = f'<s>Подсчитываю результаты...</s><break time=\"0.30s\"/><s>^Вот^ чем вам понравится заниматься:</s><break time=\"0.30s\"/><s>{buff}</s><speaker audio=marusia-sounds/marusia-sounds/game-win-3>'
                response = send_xml(request, output, speech, False)
    elif message == 'это все' or message == 'это все?':
        response = send_img(request)
    elif message == 'а как же вездеход?' or message == 'а как же вездеход':
        response = send_app(request, 'https://vk.com/app6612435')
    else:
        response = send_ans(request, 'Я вас не поняла', False)
    return web.json_response(response)


def init():
    app = web.Application()
    cors = aiohttp_cors.setup(app)
    resource = cors.add(app.router.add_resource("/webhook"))
    route = cors.add(
        resource.add_route("POST", webhook), {
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*"),
        })
    web.run_app(app, host=HOST_IP, port=HOST_PORT)


if __name__ == "__main__":
    init()
