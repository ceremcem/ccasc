# -*- coding: utf8 -*-
__author__ = 'ceremcem'
import re

import cca_logging
logger = cca_logging.logger


class cca_scyml():

    start_signal = "start"          # == open
    stop_signal = "stop"            # == close
    allow_exec_signal = "allow_exec"

    starting_state = "starting"     # == opening
    started_state = "started"       # == opened
    stopping_state = "stopping"     # == closing
    stopped_state = "stopped"       # == closed
    external_signal_requested = started_state

    @staticmethod
    def isSignal(name):
        # returns True if this is a signal method
        if (name == cca_scyml.start_signal
            or name == cca_scyml.stop_signal):
            return True
        else:
            return False

    @staticmethod
    def get_object(command):
        """
        # eş anlamlılar:
        # --------------
        # sinyal isimleri:
        #   open, start: çalış, ver, aç
        #   close, stop: dur, kes, kapat
        #
        # durum isimleri:
        #   opening, starting:  çalışmaya başlıyor,     verilmeye başlıyor,     açılıyor
        #   opened, started:    çalışıyor,              veriliyor,              açık,       var,        ""
        #   closing, stopping:  durmaya başlıyor,       kesilmeye başlıyor,     kapanıyor
        #   closed, stopped:    durdu,                  kesildi,                kapalı,     yok
        #
        # özel sinyaller:
        # --------------
        #   bekle -> örn. "3 sn bekle;"
        #
        """
        # arg func
        special_funcs = {
            "sleep" : ["bekle"],
        }

        default_signal = cca_scyml.external_signal_requested
        verbs = {
            cca_scyml.start_signal:     [u"çalış",              u"ver",                     u"aç"],
            cca_scyml.stop_signal:      [u"dur",                u"kes",                     u"kapat"],

            cca_scyml.starting_state:   [u"çalışmaya başlıyor", u"verilmeye başlıyor",      u"açılıyor"             ],
            cca_scyml.started_state:    [u"çalışıyor",          u"veriliyor",               u"açık",        u"var"  ],
            cca_scyml.stopping_state:   [u"durmaya başlıyor",   u"kesilmeye başlıyor",      u"kapanıyor"            ],
            cca_scyml.stopped_state:    [u"durdu",              u"kesildi",                 u"kapalı",      u"yok"  ],
            #cca_scyml.external_signal_requested: ["geldi"]
            }

        o = {}
        p = command.split(",")
        sentence = unicode(p[0])

        o["args"] = []
        for arg in p[1:]:
            o["args"].append(arg.strip())

        for key, verb_lists in verbs.iteritems():
            for verb in verb_lists:
                s = re.search(ur'\b' + verb + ur'\b', sentence, re.UNICODE)
                if s:
                    o["instance name"] = sentence[:s.start()].strip()
                    o["call"] = key.strip()
                    return o

        for verb in special_funcs["sleep"]:
            s = re.search(r'\b' + verb + r'\b', sentence, re.UNICODE)
            if s:
                o["instance name"] = "sleep"
                o["call"] = cca_scyml.start_signal
                o["args"].append(sentence[:s.start()].strip())
                return o

        # if there is no match, return whole sentence
        o["instance name"] = sentence
        o["call"] = default_signal
        return o
