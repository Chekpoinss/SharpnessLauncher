// SPDX-License-Identifier: GPL-3.0-only
#pragma once

#include <QJsonArray>
#include <QJsonObject>
#include <QString>

namespace Sharpness::AI {
QJsonArray tools();
QString redact(QString text);
QString executable();
QJsonObject call(const QString& dataDirectory, const QString& name, const QJsonObject& arguments, bool allowWrite = false);
int serve(int argc, char* argv[]);
}  // namespace Sharpness::AI
