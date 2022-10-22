from lib.drive import Drive

if __name__ == '__main__':
    d = Drive()
    d.copy_audio_files_to_drive('teeko', 'data/tjsp/teeko/translated/audio_subtitles.json',
                                r'C:\Program Files (x86)\Steam\steamapps\common\The Jackbox Party Starter\games\AwShirt\TalkshowExport\project\media')
    # f = Fakin()
    # f.encode_audio_subtitles()
    # q.encode_audio_subtitles()
    # g = Guesspionage()
    # g.encode_audio_subtitles()
    # import os
    # src = r'C:\Program Files (x86)\Steam\steamapps\common\The Jackbox Party Pack 3'
    # start_ts = datetime(2022, 10, 4)
    # for root, dirs, files in os.walk(src, topdown=False):
    #     for f in files:
    #         fpath = os.path.join(root, f)
    #         ts = datetime.fromtimestamp(os.path.getmtime(fpath))
    #         if ts < start_ts:
    #             print(fpath, ts)
    # crowdin project
    # c = Crowdin()
    # c.download_last_build(528716)
    # c.unzip_build()

    # TMP2
    # t = TMP2()
    # t.decode_all()

    # t.update_localization(r'C:\Program Files (x86)\Steam\steamapps\common\The Jackbox Party Starter\localization_manager.json',
    #                       'build/uk/localization_managerEN.json')
    # t.update_localization(r'C:\Program Files (x86)\Steam\steamapps\common\The Jackbox Party Starter\LocalizationPause.json',
    #                       'build/uk/LocalizationPauseEN.json')
    # t.update_localization(r'C:\Program Files (x86)\Steam\steamapps\common\The Jackbox Party Starter\Localization.json',
    #                       'build/uk/LocalizationEN-MAIN.json')
    # t.update_localization(r'C:\Program Files (x86)\Steam\steamapps\common\The Jackbox Party Starter\games\PartyPack\Localization.json',
    #                       'build/uk/LocalizationPack.json')

    # t.copy_to_release(r'C:\Program Files (x86)\Steam\steamapps\common\The Jackbox Party Starter',
    #                   r'C:\Users\админ\Desktop\Jackbox\starter-pack\jackbox-starter-pack-ua', datetime(2022, 7, 25))

    # t.decode_media_dict()
    # t.copy_rules_wordlist()
    # t.unpack_all()
    # c = Crowdin()

    # c.unzip_build()
    # c.download_last_build(528716)
    # t = TMP2()
    # t.encode_all()
    # t.decode_all()
    # q = Quiplash()
    # q.encode_audience_questions()
