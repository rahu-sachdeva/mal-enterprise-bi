/**
 * Mal Enterprise BI Foundation — Apps Script backend
 * Spreadsheet: Part 1 assessment prototype (synthetic data)
 *
 * Deploy: Deploy → New deployment → Web app
 * Execute as: Me
 * Who has access: Anyone
 */

var SHEET_IDS = {
  cards: 'executive_kpi_cards',
  monthly: 'monthly_trends',
  credit: 'credit_funnel_daily',
  conflictActive: 'conflict_active_customers',
  conflictApproval: 'conflict_approval_rate',
  dictionary: 'kpi_dictionary',
  catalog: 'self_service_datasets',
  landing: 'self_service_landing'
};

function doGet() {
  return HtmlService.createTemplateFromFile('Index')
    .evaluate()
    .setTitle('Mal Enterprise BI Foundation')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL)
    .addMetaTag('viewport', 'width=device-width, initial-scale=1');
}

function include_(filename) {
  return HtmlService.createHtmlOutputFromFile(filename).getContent();
}

/** Called from the HTML page to load all dashboard data */
function getDashboardData(market) {
  market = market || 'All';
  var ss = SpreadsheetApp.getActiveSpreadsheet();

  return {
    generatedAt: new Date().toISOString(),
    market: market,
    executiveCards: getExecutiveCards_(ss, market),
    monthlyTrends: getMonthlyTrends_(ss, market),
    creditFunnel: getCreditFunnel_(ss, market),
    creditRisk: getCreditRiskSeries_(ss, market),
    conflictActive: getConflict_(ss, SHEET_IDS.conflictActive, market),
    conflictApproval: getConflict_(ss, SHEET_IDS.conflictApproval, market),
    dictionary: sheetToObjects_(ss.getSheetByName(SHEET_IDS.dictionary)),
    catalog: sheetToObjects_(ss.getSheetByName(SHEET_IDS.catalog)),
    landing: sheetToObjects_(ss.getSheetByName(SHEET_IDS.landing))
  };
}

function getExecutiveCards_(ss, market) {
  var rows = sheetToObjects_(ss.getSheetByName(SHEET_IDS.cards));
  return rows.filter(function (r) {
    return String(r.market) === String(market) && String(r.status) === 'certified';
  });
}

function getMonthlyTrends_(ss, market) {
  var rows = sheetToObjects_(ss.getSheetByName(SHEET_IDS.monthly));
  if (market === 'All') {
    return aggregateMonthly_(rows);
  }
  return rows
    .filter(function (r) {
      return String(r.market) === String(market);
    })
    .map(normalizeMonthly_);
}

function aggregateMonthly_(rows) {
  var byMonth = {};
  rows.forEach(function (r) {
    var m = String(r.month).substring(0, 10);
    if (!byMonth[m]) {
      byMonth[m] = {
        month: m,
        active_customers_certified: 0,
        portfolio_outstanding_aed: 0,
        revenue_finance_aed: 0,
        credit_applications: 0,
        credit_approved_certified: 0,
        credit_booked: 0,
        payment_successful: 0,
        payment_attempts: 0,
        fpd_amount_aed: 0,
        first_instalment_due_aed: 0,
        dpd30_outstanding_aed: 0,
        n: 0
      };
    }
    var b = byMonth[m];
    b.active_customers_certified += num_(r.active_customers_certified);
    b.portfolio_outstanding_aed += num_(r.portfolio_outstanding_aed);
    b.revenue_finance_aed += num_(r.revenue_finance_aed);
    b.credit_applications += num_(r.credit_applications);
    b.credit_approved_certified += num_(r.credit_approved_certified);
    b.credit_booked += num_(r.credit_booked);
    b.payment_successful += num_(r.payment_successful);
    b.payment_attempts += num_(r.payment_attempts);
    b.fpd_amount_aed += num_(r.fpd_amount_aed);
    b.first_instalment_due_aed += num_(r.first_instalment_due_aed);
    b.dpd30_outstanding_aed += num_(r.dpd30_outstanding_aed);
    b.n += 1;
  });
  return Object.keys(byMonth)
    .sort()
    .map(function (k) {
      var b = byMonth[k];
      return {
        month: b.month,
        active_customers_certified: b.active_customers_certified,
        portfolio_outstanding_aed: b.portfolio_outstanding_aed,
        revenue_finance_aed: b.revenue_finance_aed,
        approval_rate_certified: safeDiv_(b.credit_approved_certified, b.credit_applications),
        booking_rate: safeDiv_(b.credit_booked, b.credit_approved_certified),
        payment_success_rate: safeDiv_(b.payment_successful, b.payment_attempts),
        fpd_rate: safeDiv_(b.fpd_amount_aed, b.first_instalment_due_aed),
        dpd30_rate: safeDiv_(b.dpd30_outstanding_aed, b.portfolio_outstanding_aed)
      };
    });
}

function normalizeMonthly_(r) {
  return {
    month: String(r.month).substring(0, 10),
    active_customers_certified: num_(r.active_customers_certified),
    portfolio_outstanding_aed: num_(r.portfolio_outstanding_aed),
    revenue_finance_aed: num_(r.revenue_finance_aed),
    approval_rate_certified: num_(r.approval_rate_certified),
    booking_rate: num_(r.booking_rate),
    payment_success_rate: num_(r.payment_success_rate),
    fpd_rate: num_(r.fpd_rate),
    dpd30_rate: num_(r.dpd30_rate)
  };
}

function getCreditFunnel_(ss, market) {
  var rows = sheetToObjects_(ss.getSheetByName(SHEET_IDS.credit));
  if (market !== 'All') {
    rows = rows.filter(function (r) {
      return String(r.market) === String(market);
    });
  }
  if (!rows.length) return { apps: 0, approved: 0, booked: 0, asOf: null };
  var maxDate = rows.reduce(function (m, r) {
    var d = String(r.date).substring(0, 10);
    return d > m ? d : m;
  }, '1970-01-01');
  var latest = rows.filter(function (r) {
    return String(r.date).substring(0, 10) === maxDate;
  });
  var apps = 0;
  var approved = 0;
  var booked = 0;
  latest.forEach(function (r) {
    apps += num_(r.credit_applications);
    approved += num_(r.credit_approved_certified);
    booked += num_(r.credit_booked);
  });
  return { apps: apps, approved: approved, booked: booked, asOf: maxDate };
}

function getCreditRiskSeries_(ss, market) {
  return getMonthlyTrends_(ss, market);
}

function getConflict_(ss, sheetName, market) {
  var rows = sheetToObjects_(ss.getSheetByName(sheetName));
  var m = market === 'All' ? 'UAE' : market;
  return rows.filter(function (r) {
    return String(r.market) === String(m);
  });
}

function sheetToObjects_(sheet) {
  if (!sheet) return [];
  var values = sheet.getDataRange().getValues();
  if (values.length < 2) return [];
  var headers = values[0].map(function (h) {
    return String(h).trim();
  });
  var out = [];
  for (var i = 1; i < values.length; i++) {
    var row = values[i];
    if (row.join('') === '') continue;
    var obj = {};
    for (var c = 0; c < headers.length; c++) {
      var v = row[c];
      if (Object.prototype.toString.call(v) === '[object Date]') {
        v = Utilities.formatDate(v, Session.getScriptTimeZone(), 'yyyy-MM-dd');
      }
      obj[headers[c]] = v;
    }
    out.push(obj);
  }
  return out;
}

function num_(v) {
  var n = Number(v);
  return isNaN(n) ? 0 : n;
}

function safeDiv_(a, b) {
  return b ? a / b : 0;
}

/** Optional: custom menu inside the spreadsheet */
function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('Mal BI')
    .addItem('Open HTML dashboard (dev)', 'openDashboardDialog_')
    .addToUi();
}

function openDashboardDialog_() {
  var html = HtmlService.createHtmlOutput(
    '<p>Deploy this project as a <b>Web app</b> (Deploy → New deployment → Web app → Anyone), ' +
      'then open the deployment URL for the live HTML report with charts.</p>'
  )
    .setWidth(420)
    .setHeight(140);
  SpreadsheetApp.getUi().showModalDialog(html, 'Mal Enterprise BI');
}
