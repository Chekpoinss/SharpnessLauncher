// SPDX-License-Identifier: GPL-3.0-only
#include <QTemporaryDir>
#include <QTest>
#include "minecraft/auth/AccountList.h"
#include "minecraft/auth/MinecraftAccount.h"

class OfflineAccountTest : public QObject {
    Q_OBJECT
   private slots:
    void firstOfflineAccountCanBeUsedWithoutMicrosoft()
    {
        AccountList accounts;
        QVERIFY(!accounts.anyAccountIsValid());
        const auto offline = MinecraftAccount::createOffline("SharpnessTest");
        accounts.addAccount(offline);
        accounts.setDefaultAccount(offline);
        QVERIFY(accounts.anyAccountIsValid());
        QCOMPARE(accounts.defaultAccount()->accountType(), AccountType::Offline);
        QVERIFY(!offline->ownsMinecraft());
    }

    void offlineAccountSurvivesRestart()
    {
        QTemporaryDir directory;
        QVERIFY(directory.isValid());
        const auto path = directory.filePath("accounts.json");
        {
            AccountList accounts;
            accounts.setListFilePath(path);
            const auto offline = MinecraftAccount::createOffline("SharpnessTest");
            accounts.addAccount(offline);
            accounts.setDefaultAccount(offline);
            QVERIFY(accounts.saveList());
        }
        AccountList restored;
        restored.setListFilePath(path);
        QVERIFY(restored.loadList());
        QVERIFY(restored.anyAccountIsValid());
        QCOMPARE(restored.count(), 1);
        QCOMPARE(restored.defaultAccount()->profileName(), QString("SharpnessTest"));
    }
};

QTEST_GUILESS_MAIN(OfflineAccountTest)
#include "OfflineAccount_test.moc"
