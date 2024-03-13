const addNewLine = (data) => {
  const parsedData = JSON.parse(new Buffer.from(data, 'base64').toString('utf8'));
  return new Buffer.from(JSON.stringify(parsedData) + '\n').toString('base64')
}

exports.fixNewline = async (event, context) => {
  const output = event.records.map((record) => ({
    recordId: record.recordId,
    result: 'Ok',
    data: addNewLine(record.data),
  }));
  return { records: output };
};
