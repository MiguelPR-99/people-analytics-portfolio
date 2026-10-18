interface BaseTableRegistrations {}
interface BaseEnumRegistrations {}

type TableRow<T> = T;

type QueryTableOptions = {
  select?: string[];
  filter?: string;
  orderBy?: string;
  pageSize?: number;
};

interface BaseUxAgentDataApi<Tables extends BaseTableRegistrations, Enums extends BaseEnumRegistrations> {
  createRow<TableName extends keyof Tables & string>(
    table: TableName,
    row: Record<string, unknown>,
  ): Promise<string>;

  queryTable<TableName extends keyof Tables & string>(
    table: TableName,
    options?: QueryTableOptions,
  ): Promise<{ rows: Tables[TableName][] }>;
}
