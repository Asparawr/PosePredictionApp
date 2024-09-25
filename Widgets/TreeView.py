import tkinter as tk
from tkinter import ttk


class TreeView(ttk.Treeview):
    def __init__(self, parent, height, row, column, rowSpan=1, columnspan=1):
        # Scrollbar
        self.treeScroll = ttk.Scrollbar(parent)
        self.treeScroll.grid(
            row=row,
            rowspan=rowSpan,
            column=column + columnspan,
            padx=(0, 5),
            pady=(10, 10),
            sticky="nsew",
        )

        super().__init__(
            parent,
            selectmode="extended",
            yscrollcommand=self.treeScroll.set,
            height=height,
        )

        self.grid(
            row=row,
            rowspan=rowSpan,
            column=column,
            columnspan=columnspan,
            padx=(10, 3),
            pady=(10, 10),
            sticky="nsew",
        )
        self.treeScroll.config(command=self.yview)


class MultiTreeView(ttk.Treeview):
    def __init__(
        self, parent, height, row, column, rowSpan=1, columnspan=1, columns=None
    ):
        # Scrollbar
        self.treeScroll = ttk.Scrollbar(parent)
        self.treeScroll.grid(
            row=row,
            rowspan=rowSpan,
            column=column + columnspan,
            padx=(0, 5),
            pady=(10, 10),
            sticky="nsew",
        )
        super().__init__(
            parent,
            selectmode="none",
            yscrollcommand=self.treeScroll.set,
            height=height,
            columns=columns,
        )
        self.treeScroll.config(command=self.yview)
        self.bind("<ButtonRelease-1>", self.select)

        self.grid(
            row=row,
            rowspan=rowSpan,
            column=column,
            columnspan=columnspan,
            padx=(10, 3),
            pady=(10, 10),
            sticky="nsew",
        )
        self.treeScroll.config(command=self.yview)

    def select(self, event=None):
        self.selection_toggle(self.focus())

    def grid_remove(self):
        self.treeScroll.grid_remove()
        super().grid_remove()

    def grid(self, **kwargs):
        self.treeScroll.grid()
        super().grid(**kwargs)
