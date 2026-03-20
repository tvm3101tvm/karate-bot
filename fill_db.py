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
            gif_path='CgACAgIAAxkBAAIHGGm8jq51-Ut4_I4Hboa6JNPJbAZmAAIxoQACYE3gSRjExR_L6_vpOgQ',
            audio_path='CQACAgIAAxkBAAIH_2m9foO5U4B6NAuTgH6KEZeHWLkEAALQlAACYE3oSUgrj-YyAoqzOgQ'
        ),
        Technique(
            name_ru='Стойка всадника',
            name_ja='Киба дачи',
            category='stance',
            description='Стойка с широко расставленными ногами.',
            video_path='file_id_видео_киба',
            gif_path='CgACAgIAAxkBAAIHSGm9W2N8JUrK47mqTn18WyEmcOFcAAKfkgACYE3oSZ4S4yhADOXnOgQ',
            audio_path='CQACAgIAAxkBAAIH_Gm9foPx5i6R1XhINexhchTrgGOrAALUlAACYE3oSZq-9Wqw2nw1OgQ'
        ),
        Technique(
            name_ru='Задняя стойка',
            name_ja='Кокуцу дачи',
            category='stance',
            description='Перенос веса на заднюю ногу.',
            video_path='BAACAgIAAxkBAAIGyGm8HZeIBMPe9EEkc0KpAqCc7pppAALKmQACbbNRSRqCOqCB_rM6OgQ',
            gif_path='CgACAgIAAxkBAAIGyWm8HxdEXaejlXw1U6dafg78BTzCAAJnngAC_T14SaLSXpRJf8NjOgQ',
            audio_path='CQACAgIAAxkBAAIH_mm9foPYoG6mjrZvZ0MdQMHmCla5AALRlAACYE3oSU1lCXZ0gDA3OgQ'
        ),

        
        Technique(
            name_ru='Верхний блок',
            name_ja='Аге-уке',
            category='block',
            description='Для защиты головы.',
            video_path='file_id_видео_агэукэ',
            gif_path='CgACAgIAAxkBAAIHFGm8jRIx697Iqn1yms6ryt4gpm11AAIinQACMzzBSbuRbL8GUw-FOgQ',
            audio_path='CQACAgIAAxkBAAIIB2m9foOgYyj4jr1HisxnCdXuLI-8AALblAACYE3oSb6T7emuYXcYOgQ'
        ),
        Technique(
            name_ru='Нижний блок',
            name_ja='Гедан барай',
            category='block',
            description='Для защиты паха и корпуса.',
            video_path='file_id_видео_гедан',
            gif_path='CgACAgIAAxkBAAIHQmm9Uo0DoDsIGvXxldbFMehxH9xqAAKbkgACYE3oSU7R1t7WB20bOgQ',
            audio_path='CQACAgIAAxkBAAIIAmm9foPTEcLup_S_-QXLXHgolRYaAALZlAACYE3oSW7ax3HmIzyxOgQ'
        ),
        Technique(
            name_ru='Внутренний блок',
            name_ja='Учи-уке',
            category='block',
            description='Блок изнутри наружу (ладонью вверх).',
            video_path='file_id_видео_учиукэ',
            gif_path='CgACAgIAAxkBAAIHRmm9W1wYLa9hJIIc3u3E2yuLzQ_MAAIHkwACYE3oSfoooOE6rc3kOgQ',
            audio_path='CQACAgIAAxkBAAIIAAFpvX6Dgrk1JRJCUxfxMRtDmZhmxAAC05QAAmBN6ElHWa693cjJizoE'
        ),
        Technique(
            name_ru='Внешний блок',
            name_ja='Сото-уке',
            category='block',
            description='Блок снаружи внутрь (ладонью вниз).',
            video_path='file_id_видео_сотоукэ',
            gif_path='CgACAgIAAxkBAAIHRGm9W1J111jYKagPiH-J1-BfJOVNAAIIkwACYE3oSRCfIG9lh6sGOgQ',
            audio_path='CQACAgIAAxkBAAIH_Wm9foNBbeVnw18LF1QxAQtVsvMnAALPlAACYE3oSc2_CkPyXt2wOgQ'
        ),
        Technique(
            name_ru='Блок ребром ладони',
            name_ja='Шуто-уке',
            category='block',
            description='Блок ребром ладони как лезвием ножа.',
            video_path='file_id_видео_шуто',
            gif_path='CgACAgIAAxkBAAIHWGm9YNvAvtJWnlTPyAWE-kx2yAl0AAIyoQACYE3gSVyUloSD6x1mOgQ',
            audio_path='CQACAgIAAxkBAAIICGm9foPIAYmXaL6TkS9B6VL3YREkAALVlAACYE3oSVRx_1dGB2-rOgQ'
        ),

        
        Technique(
            name_ru='Прямой удар (разноименный)',
            name_ja='Ой-цуки',
            category='punch',
            description='Прямой удар рукой, разноимённый с впереди стоящей ногой.',
            video_path='file_id_видео_ойцуки',
            gif_path='BAACAgIAAxkBAAIBvWmseJI4-ZgYaJON_90r0ZKKl5L8AAKPmAAChPhoSYjPqjEPFiZlOgQ',
            audio_path='CQACAgIAAxkBAAIICWm9foN59AF9mJRLaD7CYJt3_OD1AALXlAACYE3oSfMloLbHvW7mOgQ'
        ),
        Technique(
            name_ru='Прямой удар (одноименный)',
            name_ja='Гьяку-цуки',
            category='punch',
            description='Прямой удар рукой, одноимённый с впереди стоящей ногой',
            video_path='file_id_видео_гьякуцуки',
            gif_path='BAACAgIAAxkBAAIBvWmseJI4-ZgYaJON_90r0ZKKl5L8AAKPmAAChPhoSYjPqjEPFiZlOgQ',
            audio_path='CQACAgIAAxkBAAIIBGm9foMmfnGRuJyf6HhP2mwQFe9bAALclAACYE3oSQPFTkbDOVfGOgQ'
        ),

        
        Technique(
            name_ru='Прямой удар ногой',
            name_ja='Мае-гери',
            category='kick',
            description='Удар ногой вперёд.',
            video_path='file_id_видео_маэгэри',
            gif_path='CgACAgIAAxkBAAIHSGm9W2N8JUrK47mqTn18WyEmcOFcAAKfkgACYE3oSZ4S4yhADOXnOgQ',
            audio_path='CQACAgIAAxkBAAIIAWm9foNvJBVidGj6HgpvSll0QBgOAALalAACYE3oSZp_NOubXzn4OgQ'
        ),
        Technique(
            name_ru='Круговой удар ногой',
            name_ja='Маваши-гери',
            category='kick',
            description='Удар ногой по кругу.',
            video_path='file_id_видео_маваши',
            gif_path='BAACAgIAAxkBAAIBvWmseJI4-ZgYaJON_90r0ZKKl5L8AAKPmAAChPhoSYjPqjEPFiZlOgQ',
            audio_path='CQACAgIAAxkBAAIIBmm9foOHCf2bWZ_a08mvZs75ZOz-AALWlAACYE3oSRnBLex_vdtqOgQ'
        ),
        Technique(
            name_ru='Проникающий боковой удар ногой',
            name_ja='Йоко-гери кекоми',
            category='kick',
            description='Удар ребром либо пяткой стопы.',
            video_path='file_id_видео_йоко',
            gif_path='CgACAgIAAxkBAAIHIGm8lWxu56d3dRldsjHts-ibtNHWAAI_oQACYE3gSbpL9OtAIPUQOgQ',
            audio_path='CQACAgIAAxkBAAIIA2m9foN7kwvzPxVmn_SEXIPHYfwbAALSlAACYE3oScTXJ9Xr-C0qOgQ'
        ),
        Technique(
            name_ru='Обратный круговой',
            name_ja='Урамаваши-гери',
            category='kick',
            description='Круговой удар с разворотом пяткой.',
            video_path='file_id_видео_урамаваши',
            gif_path='CgACAgIAAxkBAAIHHGm8kt4VRQ5uWdotiHJvdfjbL30nAAI3oQACYE3gSfINlRzVvJeaOgQ',
            audio_path='CQACAgIAAxkBAAIIBWm9foMIfnRUys7pomg8VvV3tU8IAALYlAACYE3oSTxYu6ict1zlOgQ'
        ),
    ]

    session.add_all(techniques)
    session.commit()
    session.close()
    print(f'Добавлено {len(techniques)} техник.')

if __name__ == '__main__':
    main()