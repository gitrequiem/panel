/*!
 Column visibility buttons for Buttons and DataTables.
 2016 SpryMedia Ltd - datatables.net/license
*/
(function (h) {
  "function" === typeof define && define.amd
    ? define(
        ["jquery", "datatables.net", "datatables.net-buttons"],
        function (e) {
          return h(e, window, document);
        }
      )
    : "object" === typeof exports
    ? (module.exports = function (e, g) {
        e || (e = window);
        (g && g.fn.dataTable) || (g = require("datatables.net")(e, g).$);
        g.fn.dataTable.Buttons || require("datatables.net-buttons")(e, g);
        return h(g, e, e.document);
      })
    : h(jQuery, window, document);
})(function (h, e, g, l) {
  e = h.fn.dataTable;
  h.extend(e.ext.buttons, {
    colvis: function (b, a) {
      var c = null,
        d = {
          extend: "collection",
          init: function (f, k) {
            c = k;
          },
          text: function (f) {
            return f.i18n("buttons.colvis", "Column visibility");
          },
          className: "buttons-colvis",
          closeButton: !1,
          buttons: [
            {
              extend: "columnsToggle",
              columns: a.columns,
              columnText: a.columnText,
            },
          ],
        };
      b.on("column-reorder.dt" + a.namespace, function (f, k, m) {
        b.button(null, b.button(null, c).node()).collectionRebuild([
          {
            extend: "columnsToggle",
            columns: a.columns,
            columnText: a.columnText,
          },
        ]);
      });
      return d;
    },
    columnsToggle: function (b, a) {
      return b
        .columns(a.columns)
        .indexes()
        .map(function (c) {
          return {
            extend: "columnToggle",
            columns: c,
            columnText: a.columnText,
          };
        })
        .toArray();
    },
    columnToggle: function (b, a) {
      return {
        extend: "columnVisibility",
        columns: a.columns,
        columnText: a.columnText,
      };
    },
    columnsVisibility: function (b, a) {
      return b
        .columns(a.columns)
        .indexes()
        .map(function (c) {
          return {
            extend: "columnVisibility",
            columns: c,
            visibility: a.visibility,
            columnText: a.columnText,
          };
        })
        .toArray();
    },
    columnVisibility: {
      columns: l,
      text: function (b, a, c) {
        return c._columnText(b, c);
      },
      className: "buttons-columnVisibility",
      action: function (b, a, c, d) {
        b = a.columns(d.columns);
        a = b.visible();
        b.visible(d.visibility !== l ? d.visibility : !(a.length && a[0]));
      },
      init: function (b, a, c) {
        var d = this;
        a.attr("data-cv-idx", c.columns);
        b.on("column-visibility.dt" + c.namespace, function (f, k) {
          k.bDestroying ||
            k.nTable != b.settings()[0].nTable ||
            d.active(b.column(c.columns).visible());
        }).on("column-reorder.dt" + c.namespace, function (f, k, m) {
          c.destroying ||
            1 !== b.columns(c.columns).count() ||
            (d.text(c._columnText(b, c)),
            d.active(b.column(c.columns).visible()));
        });
        this.active(b.column(c.columns).visible());
      },
      destroy: function (b, a, c) {
        b.off("column-visibility.dt" + c.namespace).off(
          "column-reorder.dt" + c.namespace
        );
      },
      _columnText: function (b, a) {
        var c = b.column(a.columns).index(),
          d = b.settings()[0].aoColumns[c].sTitle;
        d || (d = b.column(c).header().innerHTML);
        d = d
          .replace(/\n/g, " ")
          .replace(/<br\s*\/?>/gi, " ")
          .replace(/<select(.*?)<\/select>/g, "")
          .replace(/<!\-\-.*?\-\->/g, "")
          .replace(/<.*?>/g, "")
          .replace(/^\s+|\s+$/g, "");
        return a.columnText ? a.columnText(b, c, d) : d;
      },
    },
    colvisRestore: {
      className: "buttons-colvisRestore",
      text: function (b) {
        return b.i18n("buttons.colvisRestore", "Restore visibility");
      },
      init: function (b, a, c) {
        c._visOriginal = b
          .columns()
          .indexes()
          .map(function (d) {
            return b.column(d).visible();
          })
          .toArray();
      },
      action: function (b, a, c, d) {
        a.columns().every(function (f) {
          f =
            a.colReorder && a.colReorder.transpose
              ? a.colReorder.transpose(f, "toOriginal")
              : f;
          this.visible(d._visOriginal[f]);
        });
      },
    },
    colvisGroup: {
      className: "buttons-colvisGroup",
      action: function (b, a, c, d) {
        a.columns(d.show).visible(!0, !1);
        a.columns(d.hide).visible(!1, !1);
        a.columns.adjust();
      },
      show: [],
      hide: [],
    },
  });
  return e.Buttons;
});
