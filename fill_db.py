from database import Session, Technique

def main():
    session = Session()
    
    session.query(Technique).delete()

    techniques = [
        
        Technique(
            name_ru='Передняя стойка',
            name_ja='Дзенкуцу дачи',
            category='stance',
            description='Перенос веса на переднюю ногу.', 
            video_path='file_id_видео_дзенкуцу',  
            gif_path='CgACAgIAAyEFAATfMFtyAAMEad6QlHiRkApUL_gSAAGYk8kGKZxfAAKBmwACMzzBSbAP_uNUWtV0OwQ',
            audio_path='CQACAgIAAyEFAATfMFtyAAMVad6QlI6EJBeI5A4nIUNAYaSvVg8AAtCUAAJgTehJIqfhDxtXts47BA'
        ),
        Technique(
            name_ru='Стойка всадника',
            name_ja='Киба дачи',
            category='stance',
            description='Стойка с широко расставленными ногами.',
            video_path='file_id_видео_киба',
            gif_path='CgACAgIAAyEFAATfMFtyAAMKad6QlGJKNE59S4gnXgvzh8KQopsAAiCdAAKhIvlJNs_h0gKqJzg7BA',
            audio_path='CQACAgIAAyEFAATfMFtyAAMSad6QlEOtdeCHGORpDhD3dGOzzJkAAtSUAAJgTehJP9h0YnVFgAM7BA'
        ),
        Technique(
            name_ru='Задняя стойка',
            name_ja='Кокуцу дачи',
            category='stance',
            description='Перенос веса на заднюю ногу.',
            video_path='BAACAgIAAyEFAATfMFtyAAMCad5s0aRPLjhXZCb2zj1om4Ts01oAAiaZAAKfkQFKplIJ7Akvfk07BA',
            gif_path='CgACAgIAAyEFAATfMFtyAAMDad6QlCuEEw3vQhhlTwFXgIm6DfUAAmeeAAL9PXhJklz4NTp2xB07BA',
            audio_path='CQACAgIAAyEFAATfMFtyAAMUad6QlNFfSIMiZv1Gwz3Y4boxN6YAAtGUAAJgTehJlUWg57WZ6zA7BA'
        ),

        
        Technique(
            name_ru='Верхний блок',
            name_ja='Аге уке',
            category='block',
            description='Для защиты головы.',
            video_path='file_id_видео_агэукэ',
            gif_path='CgACAgIAAyEFAATfMFtyAAMFad6QlC1n88xWYfZkgwf8gSawP_wAAiKdAAIzPMFJIm7-lXiyKjM7BA',
            audio_path='CQACAgIAAyEFAATfMFtyAAMdad6QlNcAAdmfEQKYlwVrRO6U85TOAALblAACYE3oSR_-XJbTLmGKOwQ'
        ),
        Technique(
            name_ru='Нижний блок',
            name_ja='Гедан барай',
            category='block',
            description='Для защиты паха и корпуса.',
            video_path='file_id_видео_гедан',
            gif_path='CgACAgIAAyEFAATfMFtyAAMRad6QlM0ZUybZLWhnpWOQUCulAR8AAnG0AAIiQ_BKzHJcN9enOkY7BA',
            audio_path='CQACAgIAAyEFAATfMFtyAAMYad6QlBYKxJRq7NTOgAI1NrHbnq4AAtmUAAJgTehJRceQfYGIG8s7BA'
        ),
        Technique(
            name_ru='Внутренний блок',
            name_ja='Учи уке',
            category='block',
            description='Блок изнутри наружу (ладонью вверх).',
            video_path='file_id_видео_учиукэ',
            gif_path='CgACAgIAAyEFAATfMFtyAAMIad6QlGofjxqnsueA31uCSYVy_vcAAgeTAAJgTehJkgABnyy_SMjlOwQ',
            audio_path='CQACAgIAAyEFAATfMFtyAAMWad6QlGzIJNWPkVYnv18-hLLl1EMAAtOUAAJgTehJJnb9O935XdU7BA'
        ),
        Technique(
            name_ru='Внешний блок',
            name_ja='Сото уке',
            category='block',
            description='Блок снаружи внутрь (ладонью вниз).',
            video_path='file_id_видео_сотоукэ',
            gif_path='CgACAgIAAyEFAATfMFtyAAMJad6QlPMxasRPtbAHioe8SbQtHJ4AAgiTAAJgTehJyJI3rM5xCZE7BA',
            audio_path='CQACAgIAAyEFAATfMFtyAAMTad6QlBLVzcMHwrZ1Ism0C8RQ0UIAAs-UAAJgTehJgcYTEkZ18lg7BA'
        ),
        Technique(
            name_ru='Блок ребром ладони',
            name_ja='Шуто уке',
            category='block',
            description='Блок ребром ладони как лезвием ножа.',
            video_path='file_id_видео_шуто',
            gif_path='CgACAgIAAyEFAATfMFtyAAMGad6QlLcQlx903hdQwAyWZIWu0QQAAjKhAAJgTeBJFH6NJWFayoc7BA',
            audio_path='CQACAgIAAyEFAATfMFtyAAMead6QlGq6I4acFFg5xeKuL-50ngoAAtWUAAJgTehJJ9P3G9mcKG47BA'
        ),

        
        Technique(
            name_ru='Прямой удар (разноименный)',
            name_ja='Ой цуки',
            category='punch',
            description='Прямой удар рукой, разноимённый с впереди стоящей ногой.',
            video_path='file_id_видео_ойцуки',
            gif_path='CgACAgIAAyEFAATfMFtyAAMMad6QlMHNtVpAEcBFiIIY3HtxszoAAiO0AAIiQ_BK1283zJeO7SQ7BA',
            audio_path='CQACAgIAAyEFAATfMFtyAAMaad6QlKnm5S5Vc8hNW93z6SQ5n6sAAtyUAAJgTehJlEWl7RNI85U7BA'
        ),
        Technique(
            name_ru='Прямой удар (одноименный)',
            name_ja='Гьяку цуки',
            category='punch',
            description='Прямой удар рукой, одноимённый с впереди стоящей ногой',
            video_path='file_id_видео_гьякуцуки',
            gif_path='CgACAgIAAyEFAATfMFtyAAMLad6QlF3KhE_m7_f_5z_X2EhGrwADHrQAAiJD8EqnlzYtlTk2LzsE',
            audio_path='CQACAgIAAyEFAATfMFtyAAMfad6QlCBUtjCVrhgvd9LMKAyraI8AAteUAAJgTehJnznbwyFDa5A7BA'
        ),

        
        Technique(
            name_ru='Прямой удар ногой',
            name_ja='Мае гери',
            category='kick',
            description='Удар ногой вперёд.',
            video_path='file_id_видео_маэгэри',
            gif_path='CgACAgIAAyEFAATfMFtyAAMPad6QlBMetmZqttFtyfxujxH18_AAAp-SAAJgTehJAaIrXwglaX87BA',
            audio_path='CQACAgIAAyEFAATfMFtyAAMXad6QlIzfYISzh0S0E93OzZLg4jEAAtqUAAJgTehJORkBPL21akI7BA'
        ),
        Technique(
            name_ru='Круговой удар ногой',
            name_ja='Маваши гери',
            category='kick',
            description='Удар ногой по кругу.',
            video_path='file_id_видео_маваши',
            gif_path='CgACAgIAAyEFAATfMFtyAAMQad6QlF9gCUCJUErnlVu_K9Hw6KsAAmyfAAKhIvlJFhiJ3AIjjDc7BA',
            audio_path='CQACAgIAAyEFAATfMFtyAAMcad6QlFtrd7oGqjmKlkVs4Y8FNsMAAtaUAAJgTehJzB5I6L1N9uk7BA'
        ),
        Technique(
            name_ru='Проникающий боковой удар ногой',
            name_ja='Йоко гери кекоми',
            category='kick',
            description='Удар ребром либо пяткой стопы.',
            video_path='file_id_видео_йоко',
            gif_path='CgACAgIAAyEFAATfMFtyAAMOad6QlGATQL8ue_qkFNpQeOxGnqMAAj-hAAJgTeBJT0Me1uZLa7g7BA',
            audio_path='CQACAgIAAyEFAATfMFtyAAMZad6QlLIJONwc8_x-Pt7aijYk9A8AAtKUAAJgTehJKW7EIK4v4IM7BA'
        ),
        Technique(
            name_ru='Обратный круговой',
            name_ja='Урамаваши гери',
            category='kick',
            description='Круговой удар с разворотом пяткой.',
            video_path='file_id_видео_урамаваши',
            gif_path='CgACAgIAAyEFAATfMFtyAAMNad6QlEICEqPCPMghXtAqPRb0QBMAAjehAAJgTeBJHTa8x0AKlck7BA',
            audio_path='CQACAgIAAyEFAATfMFtyAAMbad6QlPgSgX7tGxV_-ZsRYtkLwpMAAtiUAAJgTehJIFFRUo9P8dQ7BA'
        ),
    ]

    session.add_all(techniques)
    session.commit()
    session.close()
    print(f'Добавлено {len(techniques)} техник.')

if __name__ == '__main__':
    main()