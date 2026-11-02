// SPDX-License-Identifier: GPL-3.0-only
#pragma once
#include <QUrl>
#include <QWidget>
#include "ui/pages/BasePage.h"

class QCheckBox;
class QComboBox;
class QLabel;
class QLineEdit;
class QNetworkAccessManager;
class QNetworkReply;
class QPlainTextEdit;
class QPushButton;
class QTabWidget;

class AiPage : public QWidget, public BasePage {
    Q_OBJECT
   public:
    explicit AiPage(QWidget* parent = nullptr);
    QString id() const override { return "ai"; }
    QString displayName() const override { return tr("AI"); }
    QIcon icon() const override { return QIcon::fromTheme("sharpness-ai", QIcon(":/icons/multimc/scalable/sharpness-ai.svg")); }
    bool apply() override;

   private:
    QString context() const;
    QUrl providerUrl();
    void send();
    QTabWidget* m_tabs;
    QLineEdit *m_endpoint, *m_model, *m_key;
    QComboBox* m_instances;
    QCheckBox* m_logs;
    QPlainTextEdit *m_question, *m_answer;
    QLabel* m_status;
    QPushButton *m_send, *m_cancel;
    QNetworkAccessManager* m_network;
    QNetworkReply* m_reply = nullptr;
};
