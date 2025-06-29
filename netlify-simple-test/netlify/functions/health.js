exports.handler = async (event, context) => {
  return {
    statusCode: 200,
    headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*'
    },
    body: JSON.stringify({
      status: 'OK',
      message: '🎉 API正常工作！',
      timestamp: new Date().toISOString()
    })
  };
};
