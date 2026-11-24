"""Tests: drafting app translations with Sunbird AI (network always mocked)."""
import json
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from ai_engine.management.commands.translate_app_text import translation_problem

RIGHTS_TS = """
const guide = {
  title: {
    en: 'Market vendors',
    lg: 'Abasuubuzi b’akatale',
  },
  law: {
    en: 'Section 18(4) of the Markets Act, 2023 says registration is free.',
    lg: 'Ekitundu 18(4) kya Markets Act, 2023 kigamba nti kwa bwereere.',
  },
  source: {
    en: 'Markets Act, 2023, Act 7 of 2023',
    lg: 'Markets Act, 2023, Act 7 of 2023',
  },
};
"""


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


@pytest.fixture
def mobile(tmp_path, settings):
    settings.SUNBIRD_API_TOKEN = 'sunbird-test-token-123'
    settings.SUNBIRD_API_URL = 'https://api.sunbird.ai'
    locales = tmp_path / 'i18n' / 'locales'
    write_json(locales / 'en.json', {'appName': 'LegalBridge', 'yes': 'Yes', 'search': 'Search', 'login': 'Log In'})
    write_json(locales / 'lg.json', {'appName': 'LegalBridge', 'yes': 'Yee', 'search': 'Noonya', 'login': 'Yingira'})
    write_json(locales / 'lgg.json', {'yes': 'Existing'})
    (tmp_path / 'constants').mkdir()
    (tmp_path / 'constants' / 'LegalRights.ts').write_text(RIGHTS_TS, encoding='utf-8')
    return tmp_path


def sunbird_reply(text, status=200, headers=None):
    response = MagicMock(status_code=status, headers=headers or {}, text='')
    response.json.return_value = {'status': 'COMPLETED', 'output': {'translated_text': text}}
    return response


def fake_translate(url, json=None, headers=None, timeout=None):
    return sunbird_reply(f"[{json['target_language']}] {json['text']}")


def run(mobile, *args):
    out = StringIO()
    call_command('translate_app_text', '--mobile-dir', str(mobile), '--delay', '0', *args, stdout=out)
    return out.getvalue()


def test_fills_only_missing_strings_and_skips_names(mobile):
    with patch('requests.post', side_effect=fake_translate) as post:
        run(mobile, '--language', 'lgg')

    ui = read_json(mobile / 'i18n' / 'locales' / 'lgg.json')
    assert ui == {'yes': 'Existing', 'search': '[lgg] Search', 'login': '[lgg] Log In'}
    assert list(ui) == ['yes', 'search', 'login']  # same order as English

    guides = read_json(mobile / 'i18n' / 'content' / 'lgg.json')
    assert guides == {
        'Market vendors': '[lgg] Market vendors',
        'Section 18(4) of the Markets Act, 2023 says registration is free.':
            '[lgg] Section 18(4) of the Markets Act, 2023 says registration is free.',
    }  # the Act's official title is not translated

    sent = [call.kwargs['json'] for call in post.call_args_list]
    assert all(body['source_language'] == 'eng' and body['target_language'] == 'lgg' for body in sent)
    assert 'LegalBridge' not in [body['text'] for body in sent]
    assert post.call_args.kwargs['headers'] == {'Authorization': 'Bearer sunbird-test-token-123'}
    assert post.call_args.args[0] == 'https://api.sunbird.ai/tasks/translate'


def test_overwrite_replaces_existing(mobile):
    with patch('requests.post', side_effect=fake_translate):
        run(mobile, '--language', 'lgg', '--overwrite')
    assert read_json(mobile / 'i18n' / 'locales' / 'lgg.json')['yes'] == '[lgg] Yes'


def test_dry_run_and_limit_save_nothing(mobile):
    with patch('requests.post', side_effect=fake_translate) as post:
        output = run(mobile, '--language', 'ach', '--limit', '1', '--dry-run')
    assert post.call_count == 1
    assert 'would save 1' in output
    assert not (mobile / 'i18n' / 'locales' / 'ach.json').exists()


def test_translation_dropping_numbers_or_names_is_not_saved(mobile):
    def lossy(url, json=None, **kwargs):
        return sunbird_reply('Ekiragiro kigamba nti kwa bwereere.')  # no section number or Act name

    with patch('requests.post', side_effect=lossy):
        output = run(mobile, '--language', 'nyn')

    guides = read_json(mobile / 'i18n' / 'content' / 'nyn.json')
    assert 'Section 18(4) of the Markets Act, 2023 says registration is free.' not in guides
    assert 'numbers missing: 4, 18, 2023' in output


def test_act_names_are_quoted_and_a_bad_translation_is_retried(mobile):
    law = 'Section 18(4) of the Markets Act, 2023 says registration is free.'
    attempts = []

    def flaky(url, json=None, **kwargs):
        if '18(4)' not in json['text']:
            return sunbird_reply(f"[x] {json['text']}")
        attempts.append(json['text'])
        if len(attempts) == 1:
            return sunbird_reply('Esele 18(4), 2023 ri ota suku ni')  # Act name translated away
        return sunbird_reply('Esele 18(4) “Markets Act”, 2023 ri')

    with patch('requests.post', side_effect=flaky):
        run(mobile, '--language', 'lgg')

    assert attempts == [law.replace('Markets Act', '"Markets Act"')] * 2
    guides = read_json(mobile / 'i18n' / 'content' / 'lgg.json')
    assert guides[law] == 'Esele 18(4) Markets Act, 2023 ri'


def test_names_are_hidden_behind_codes_on_the_last_try(mobile):
    law = 'Section 18(4) of the Markets Act, 2023 says registration is free.'
    sent = []

    def name_dropper(url, json=None, **kwargs):
        if '18(4)' not in json['text']:
            return sunbird_reply(f"[x] {json['text']}")
        sent.append(json['text'])
        if 'X1' in json['text']:
            return sunbird_reply('Esele 18(4) X1, 2023 ri')
        return sunbird_reply('Esele 18(4) azita cuu, 2023 ri')  # always translates the name

    with patch('requests.post', side_effect=name_dropper):
        run(mobile, '--language', 'lgg')

    assert sent[-1] == law.replace('Markets Act', 'X1')
    guides = read_json(mobile / 'i18n' / 'content' / 'lgg.json')
    assert guides[law] == 'Esele 18(4) Markets Act, 2023 ri'


def test_translation_problem_rules():
    assert translation_problem('Pay UGX 50,000 within 14 days', 'Sasula UGX 50,000 omu biro 14') is None
    assert translation_problem('Call LegalBridge', 'Teera') == 'names missing: LegalBridge'
    assert translation_problem('Hello', '  ') == 'empty translation'


def test_retries_when_rate_limited(mobile):
    replies = [sunbird_reply('', status=429, headers={'Retry-After': '0'})] + [sunbird_reply('ok')] * 10
    with patch('requests.post', side_effect=replies) as post, \
            patch('ai_engine.management.commands.translate_app_text.time.sleep'):
        run(mobile, '--language', 'ach', '--limit', '1')
    assert post.call_count == 2


def test_requires_token(mobile, settings):
    settings.SUNBIRD_API_TOKEN = ''
    with patch('requests.post') as post, pytest.raises(CommandError, match='SUNBIRD_API_TOKEN'):
        run(mobile, '--language', 'lgg')
    post.assert_not_called()


def test_check_reports_coverage_without_network(mobile):
    with patch('requests.post') as post:
        output = run(mobile, '--check', '--language', 'lgg')
    post.assert_not_called()
    assert 'screens: 1/3 translated' in output
    assert 'rights guides: 0/2 translated' in output
