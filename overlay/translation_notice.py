"""Add the selected language's translation disclosure to the Material footer."""

NOTICE = (
    '本文由大语言模型翻译，可能有误。'
    '<a class="translation-feedback" href="https://github.com/spaceqat/fatqat-doc-translator/issues">'
    '发现翻译问题？点此反馈</a>'
)


def on_config(config, **kwargs):
    notice = NOTICE
    if config["theme"].get("language") == "ko":
        notice = ('이 문서는 대규모 언어 모델로 번역했으며 오류가 있을 수 있습니다. '
                  '<a class="translation-feedback" href="https://github.com/spaceqat/fatqat-doc-translator/issues">'
                  '번역 오류 제보</a>')
    copyright = config.get("copyright", "")
    config["copyright"] = f"{copyright}<br>{notice}" if copyright else notice
    return config
