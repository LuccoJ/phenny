#!/usr/bin/env python3
"""
apertium_wiki.py - Phenny Apertium Wiki Stats Module
"""

import os
import requests
import shlex
import subprocess
import urllib.request
import urllib.error
from web import REQUEST_TIMEOUT
from tools import dot_path

BOT = ('https://svn.code.sf.net/p/apertium/svn/trunk/apertium-tools/wiki-tools/bot.py', 'apertium_wikistats_bot.py')
LEXCCOUNTER = ('https://svn.code.sf.net/p/apertium/svn/trunk/apertium-tools/lexccounter.py', 'lexccounter.py')

BOT_AUTOCOVERAGE = ('/bot_autocoverage.py', 'bot_autocoverage.py')
AUTOCOVERAGE = ('https://svn.code.sf.net/p/apertium/svn/trunk/apertium-tools/autocoverage.py', 'autocoverage.py')

IS_COVERAGE_RUNNING = ''

def setup(phenny):
    for files in [BOT, LEXCCOUNTER, AUTOCOVERAGE]:
        r = requests.get(files[0], timeout=REQUEST_TIMEOUT)
        if r.status_code == 200:
            with open(dot_path(files[1]), 'wb') as f:
                for chunk in r.iter_content():
                    f.write(chunk)

def awikstats(phenny, input):
    """Issue commands to the Apertium Stem Counter Bot."""

    if (not hasattr(phenny.config, 'stemCounterBotLogin') or
        not hasattr(phenny.config, 'stemCounterBotPassword')):
        phenny.say('Bot login/password needs to be set in configuration file (default.py).')
        phenny.say('Keys are stemCounterBotLogin and stemCounterBotPassword.')
        return

    botLogin = phenny.config.stemCounterBotLogin
    botPassword = phenny.config.stemCounterBotPassword

    try:
        rawInput = input.group()
        option = rawInput.split(' ')[1].strip()
    except:
        phenny.say('Invalid .awikstats command; try something like %s' % repr(awikstats.example_update))
        return

    if option == 'update':
        try:
            langs = ''.join(rawInput.split(' ')[2:]).split(',')
        except:
            phenny.say('Invalid .awikstats update command; try something like %s' % repr(awikstats.example_update))
            return

        commands = shlex.split('python3 %s %s "%s" dict -p %s -r "%s"' % (BOT[1], botLogin, botPassword, ' '.join(langs), input.nick))
        process = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=dot_path(''))
        stdout, stderr = process.communicate()

        for line in stderr.splitlines():
            phenny.msg(input.nick, line)
    elif option == 'coverage':
        global IS_COVERAGE_RUNNING

        if IS_COVERAGE_RUNNING == '':
            try:
                lang = rawInput.split(' ')[2].strip()
            except:
                phenny.say('Invalid .awikstats coverage command; try something like %s' % repr(awikstats.example_coverage))
                return

            try:
                urllib.request.urlopen('http://wiki.apertium.org/wiki/Apertium-' + lang)
            except urllib.error.HTTPError:
                phenny.say('%s: No wiki for specified language!' % input.nick)
                return

            phenny.say('%s: Calculating coverage... It may take a while, I will inform you after it\'s completed.' % input.nick)

            commands = shlex.split('python3 %s %s "%s" coverage -p %s -r "%s"' % (BOT[1], botLogin, botPassword, lang, input.nick))
            IS_COVERAGE_RUNNING = lang
            process = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=dot_path(''))
            stdout, stderr = process.communicate()
            IS_COVERAGE_RUNNING = ''

            try:
                out = stdout.splitlines()[-1].decode('utf-8').strip()
                if out.startswith('Coverage:'):
                    phenny.msg(input.nick, '%s - http://wiki.apertium.org/wiki/Apertium-%s/stats' % (out, lang))
                else:
                    for line in stderr.splitlines():
                        phenny.msg(input.nick, line)
            except:
                for line in stderr.splitlines():
                    phenny.msg(input.nick, line)
        else:
            phenny.say('%s: Sorry, there is already %s coverage running, try again after it\'s completed!' % (input.nick, IS_COVERAGE_RUNNING))
    else:
        phenny.say('Invalid .awikstats option: %s' % option)
        return

awikstats.commands = ['awikstats']
awikstats.example_update = '.awikstats update tat, kaz, tat-kaz'
awikstats.example_coverage = '.awikstats coverage tyv'
awikstats.priority = 'high'
