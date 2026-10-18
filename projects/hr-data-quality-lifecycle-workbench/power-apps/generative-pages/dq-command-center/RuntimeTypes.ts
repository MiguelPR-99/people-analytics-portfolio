// ---------------- Type Definitions which can be imported from ./RuntimeTypes -------------------------
export interface TableRegistrations extends BaseTableRegistrations {
    "environmentvariabledefinition": environmentvariabledefinition,
    "environmentvariablevalue": environmentvariablevalue,
    "mprpa_dqcaseactivity": mprpa_dqcaseactivity,
    "mprpa_dqcaseevidence": mprpa_dqcaseevidence,
    "mprpa_dqexceptionreference": mprpa_dqexceptionreference,
    "mprpa_dqremediationcase": mprpa_dqremediationcase,
    "mprpa_dqstatus": mprpa_dqstatus,
}
export interface EnumRegistrations extends BaseEnumRegistrations {
    "environmentvariabledefinition-componentstate": environmentvariabledefinition_componentstate,
    "environmentvariabledefinition-ismanaged": environmentvariabledefinition_ismanaged,
    "environmentvariabledefinition-isrequired": environmentvariabledefinition_isrequired,
    "environmentvariabledefinition-secretstore": environmentvariabledefinition_secretstore,
    "environmentvariabledefinition-statecode": environmentvariabledefinition_statecode,
    "environmentvariabledefinition-statuscode": environmentvariabledefinition_statuscode,
    "environmentvariabledefinition-type": environmentvariabledefinition_type,
    "environmentvariablevalue-componentstate": environmentvariablevalue_componentstate,
    "environmentvariablevalue-ismanaged": environmentvariablevalue_ismanaged,
    "environmentvariablevalue-statecode": environmentvariablevalue_statecode,
    "environmentvariablevalue-statuscode": environmentvariablevalue_statuscode,
    "mprpa_dqcaseactivity-mprpa_activitytype": mprpa_dqcaseactivity_mprpa_activitytype,
    "mprpa_dqcaseactivity-mprpa_systemgenerated": mprpa_dqcaseactivity_mprpa_systemgenerated,
    "mprpa_dqcaseactivity-statecode": mprpa_dqcaseactivity_statecode,
    "mprpa_dqcaseactivity-statuscode": mprpa_dqcaseactivity_statuscode,
    "mprpa_dqcaseevidence-mprpa_evidencetype": mprpa_dqcaseevidence_mprpa_evidencetype,
    "mprpa_dqcaseevidence-mprpa_supportsclosure": mprpa_dqcaseevidence_mprpa_supportsclosure,
    "mprpa_dqcaseevidence-statecode": mprpa_dqcaseevidence_statecode,
    "mprpa_dqcaseevidence-statuscode": mprpa_dqcaseevidence_statuscode,
    "mprpa_dqexceptionreference-mprpa_operationalseverity": mprpa_dqexceptionreference_mprpa_operationalseverity,
    "mprpa_dqexceptionreference-statecode": mprpa_dqexceptionreference_statecode,
    "mprpa_dqexceptionreference-statuscode": mprpa_dqexceptionreference_statuscode,
    "mprpa_dqremediationcase-mprpa_approvaloutcome": mprpa_dqremediationcase_mprpa_approvaloutcome,
    "mprpa_dqremediationcase-mprpa_evidencecomplete": mprpa_dqremediationcase_mprpa_evidencecomplete,
    "mprpa_dqremediationcase-mprpa_resolutiontype": mprpa_dqremediationcase_mprpa_resolutiontype,
    "mprpa_dqremediationcase-mprpa_sourcecorrectionstate": mprpa_dqremediationcase_mprpa_sourcecorrectionstate,
    "mprpa_dqremediationcase-statecode": mprpa_dqremediationcase_statecode,
    "mprpa_dqremediationcase-statuscode": mprpa_dqremediationcase_statuscode,
    "mprpa_dqstatus-mprpa_available": mprpa_dqstatus_mprpa_available,
    "mprpa_dqstatus-mprpa_initial": mprpa_dqstatus_mprpa_initial,
    "mprpa_dqstatus-mprpa_requiresapproval": mprpa_dqstatus_mprpa_requiresapproval,
    "mprpa_dqstatus-mprpa_requirescomment": mprpa_dqstatus_mprpa_requirescomment,
    "mprpa_dqstatus-mprpa_requiresevidence": mprpa_dqstatus_mprpa_requiresevidence,
    "mprpa_dqstatus-mprpa_terminal": mprpa_dqstatus_mprpa_terminal,
    "mprpa_dqstatus-statecode": mprpa_dqstatus_statecode,
    "mprpa_dqstatus-statuscode": mprpa_dqstatus_statuscode,
}
export type environmentvariabledefinition = TableRow<{
    // Primary Key Column
    readonly environmentvariabledefinitionid: string,
    apiid: string,
    readonly componentstate: environmentvariabledefinition_componentstate,
    readonly createdbyname: string,
    readonly createdbyyominame: string,
    readonly createdonbehalfbyname: string,
    readonly createdonbehalfbyyominame: string,
    defaultvalue: string,
    description: string,
    displayname: string,
    readonly environmentvariabledefinitionidunique: string,
    hint: string,
    inputcontrolconfig: string,
    readonly introducedversion: string,
    readonly ismanaged: environmentvariabledefinition_ismanaged,
    isrequired: environmentvariabledefinition_isrequired,
    learnmoreurl: string,
    readonly modifiedbyname: string,
    readonly modifiedbyyominame: string,
    readonly modifiedonbehalfbyname: string,
    readonly modifiedonbehalfbyyominame: string,
    readonly overwritetime: Date,
    readonly owningbusinessunitname: string,
    parameterkey: string,
    // Foreign Key Column
    _parentdefinitionid_value: `/environmentvariabledefinition(${string})`,
    readonly parentdefinitionidname: string,
    readonly schemaname: string,
    readonly secretstore: environmentvariabledefinition_secretstore,
    readonly solutionid: string,
    statecode: environmentvariabledefinition_statecode,
    statuscode: environmentvariabledefinition_statuscode,
    readonly supportingsolutionid: string,
    readonly type: environmentvariabledefinition_type,
    valueschema: string,
}>

export type environmentvariablevalue = TableRow<{
    // Primary Key Column
    readonly environmentvariablevalueid: string,
    readonly componentstate: environmentvariablevalue_componentstate,
    readonly createdbyname: string,
    readonly createdbyyominame: string,
    readonly createdonbehalfbyname: string,
    readonly createdonbehalfbyyominame: string,
    // Foreign Key Column
    readonly _environmentvariabledefinitionid_value: `/environmentvariabledefinition(${string})`,
    readonly environmentvariabledefinitionidname: string,
    readonly environmentvariablevalueidunique: string,
    readonly introducedversion: string,
    readonly ismanaged: environmentvariablevalue_ismanaged,
    readonly modifiedbyname: string,
    readonly modifiedbyyominame: string,
    readonly modifiedonbehalfbyname: string,
    readonly modifiedonbehalfbyyominame: string,
    readonly overwritetime: Date,
    schemaname: string,
    readonly solutionid: string,
    statecode: environmentvariablevalue_statecode,
    statuscode: environmentvariablevalue_statuscode,
    readonly supportingsolutionid: string,
    value: string,
}>

export type mprpa_dqcaseactivity = TableRow<{
    // Primary Key Column
    readonly mprpa_dqcaseactivityid: string,
    readonly createdbyname: string,
    readonly createdbyyominame: string,
    readonly createdonbehalfbyname: string,
    readonly createdonbehalfbyyominame: string,
    readonly modifiedbyname: string,
    readonly modifiedbyyominame: string,
    readonly modifiedonbehalfbyname: string,
    readonly modifiedonbehalfbyyominame: string,
    mprpa_activitynote: string,
    mprpa_activitynumber: string,
    mprpa_activitytitle: string,
    mprpa_activitytype: mprpa_dqcaseactivity_mprpa_activitytype,
    // Foreign Key Column
    _mprpa_fromstatus_value: `/mprpa_dqstatus(${string})`,
    readonly mprpa_fromstatusname: string,
    mprpa_occurredat: Date,
    // Foreign Key Column
    _mprpa_remediationcase_value: `/mprpa_dqremediationcase(${string})`,
    readonly mprpa_remediationcasename: string,
    mprpa_systemgenerated: mprpa_dqcaseactivity_mprpa_systemgenerated,
    // Foreign Key Column
    _mprpa_tostatus_value: `/mprpa_dqstatus(${string})`,
    readonly mprpa_tostatusname: string,
    readonly owningbusinessunitname: string,
    statecode: mprpa_dqcaseactivity_statecode,
    statuscode: mprpa_dqcaseactivity_statuscode,
}>

export type mprpa_dqcaseevidence = TableRow<{
    // Primary Key Column
    readonly mprpa_dqcaseevidenceid: string,
    readonly createdbyname: string,
    readonly createdbyyominame: string,
    readonly createdonbehalfbyname: string,
    readonly createdonbehalfbyyominame: string,
    readonly modifiedbyname: string,
    readonly modifiedbyyominame: string,
    readonly modifiedonbehalfbyname: string,
    readonly modifiedonbehalfbyyominame: string,
    readonly mprpa_evidencefile_name: string,
    mprpa_evidencenote: string,
    mprpa_evidencenumber: string,
    mprpa_evidencetitle: string,
    mprpa_evidencetype: mprpa_dqcaseevidence_mprpa_evidencetype,
    mprpa_evidenceurl: string,
    // Foreign Key Column
    _mprpa_remediationcase_value: `/mprpa_dqremediationcase(${string})`,
    readonly mprpa_remediationcasename: string,
    mprpa_supportsclosure: mprpa_dqcaseevidence_mprpa_supportsclosure,
    readonly owningbusinessunitname: string,
    statecode: mprpa_dqcaseevidence_statecode,
    statuscode: mprpa_dqcaseevidence_statuscode,
}>

export type mprpa_dqexceptionreference = TableRow<{
    // Primary Key Column
    readonly mprpa_dqexceptionreferenceid: string,
    readonly createdbyname: string,
    readonly createdbyyominame: string,
    readonly createdonbehalfbyname: string,
    readonly createdonbehalfbyyominame: string,
    readonly modifiedbyname: string,
    readonly modifiedbyyominame: string,
    readonly modifiedonbehalfbyname: string,
    readonly modifiedonbehalfbyyominame: string,
    mprpa_businesskey: string,
    mprpa_exceptionfingerprint: string,
    mprpa_exceptioninstanceid: string,
    mprpa_exceptionlabel: string,
    mprpa_expectedcondition: string,
    mprpa_fabricevaluatedat: Date,
    mprpa_fabricrunid: string,
    mprpa_fieldscope: string,
    mprpa_observedvalue: string,
    mprpa_operationalseverity: mprpa_dqexceptionreference_mprpa_operationalseverity,
    mprpa_ownerdomain: string,
    mprpa_qualitydimension: string,
    mprpa_recurrencekey: string,
    mprpa_rulecode: string,
    mprpa_rulename: string,
    mprpa_slabusinessdays: number,
    mprpa_snapshotdate: Date,
    mprpa_sourcesystem: string,
    // Foreign Key Column
    readonly _organizationid_value: `/organization(${string})`,
    readonly organizationidname: string,
    statecode: mprpa_dqexceptionreference_statecode,
    statuscode: mprpa_dqexceptionreference_statuscode,
}>

export type mprpa_dqremediationcase = TableRow<{
    // Primary Key Column
    readonly mprpa_dqremediationcaseid: string,
    readonly createdbyname: string,
    readonly createdbyyominame: string,
    readonly createdonbehalfbyname: string,
    readonly createdonbehalfbyyominame: string,
    readonly modifiedbyname: string,
    readonly modifiedbyyominame: string,
    readonly modifiedonbehalfbyname: string,
    readonly modifiedonbehalfbyyominame: string,
    mprpa_approvaloutcome: mprpa_dqremediationcase_mprpa_approvaloutcome,
    mprpa_approvalrequestedat: Date,
    mprpa_approvalrequestid: string,
    mprpa_casenumber: string,
    // Foreign Key Column
    _mprpa_casestatus_value: `/mprpa_dqstatus(${string})`,
    readonly mprpa_casestatusname: string,
    mprpa_casetitle: string,
    mprpa_dueat: Date,
    mprpa_evidencecomplete: mprpa_dqremediationcase_mprpa_evidencecomplete,
    mprpa_exceptioninstanceid: string,
    // Foreign Key Column
    _mprpa_exceptionreference_value: `/mprpa_dqexceptionreference(${string})`,
    readonly mprpa_exceptionreferencename: string,
    mprpa_lastnotifiedownerid: string,
    mprpa_lasttransitionat: Date,
    mprpa_recurrencekey: string,
    mprpa_resolutionsummary: string,
    mprpa_resolutiontype: mprpa_dqremediationcase_mprpa_resolutiontype,
    mprpa_resolvedat: Date,
    mprpa_slastartat: Date,
    mprpa_sourcecorrectionsnapshot: Date,
    mprpa_sourcecorrectionstate: mprpa_dqremediationcase_mprpa_sourcecorrectionstate,
    mprpa_triagesummary: string,
    readonly owningbusinessunitname: string,
    statecode: mprpa_dqremediationcase_statecode,
    statuscode: mprpa_dqremediationcase_statuscode,
}>

export type mprpa_dqstatus = TableRow<{
    // Primary Key Column
    readonly mprpa_dqstatusid: string,
    readonly createdbyname: string,
    readonly createdbyyominame: string,
    readonly createdonbehalfbyname: string,
    readonly createdonbehalfbyyominame: string,
    readonly modifiedbyname: string,
    readonly modifiedbyyominame: string,
    readonly modifiedonbehalfbyname: string,
    readonly modifiedonbehalfbyyominame: string,
    mprpa_available: mprpa_dqstatus_mprpa_available,
    mprpa_initial: mprpa_dqstatus_mprpa_initial,
    mprpa_requiresapproval: mprpa_dqstatus_mprpa_requiresapproval,
    mprpa_requirescomment: mprpa_dqstatus_mprpa_requirescomment,
    mprpa_requiresevidence: mprpa_dqstatus_mprpa_requiresevidence,
    mprpa_sequence: number,
    mprpa_statuscode: string,
    mprpa_statusname: string,
    mprpa_terminal: mprpa_dqstatus_mprpa_terminal,
    // Foreign Key Column
    readonly _organizationid_value: `/organization(${string})`,
    readonly organizationidname: string,
    statecode: mprpa_dqstatus_statecode,
    statuscode: mprpa_dqstatus_statuscode,
}>

const enum environmentvariabledefinition_componentstate {
"Publicado" = 0,
"Sin publicar" = 1,
"Eliminado" = 2,
"Eliminados sin publicar" = 3,
}
const enum environmentvariabledefinition_ismanaged {
"No administrado" = 0,
"Administrado" = 1,
}
const enum environmentvariabledefinition_isrequired {
"No" = 0,
"Yes" = 1,
}
const enum environmentvariabledefinition_secretstore {
"Azure Key Vault" = 0,
"Microsoft Dataverse" = 1,
}
const enum environmentvariabledefinition_statecode {
"Active" = 0,
"Inactive" = 1,
}
const enum environmentvariabledefinition_statuscode {
"Active" = 1,
"Inactive" = 2,
}
const enum environmentvariabledefinition_type {
"String" = 100000000,
"Number" = 100000001,
"Boolean" = 100000002,
"JSON" = 100000003,
"Data Source" = 100000004,
"Secret" = 100000005,
}
const enum environmentvariablevalue_componentstate {
"Publicado" = 0,
"Sin publicar" = 1,
"Eliminado" = 2,
"Eliminados sin publicar" = 3,
}
const enum environmentvariablevalue_ismanaged {
"No administrado" = 0,
"Administrado" = 1,
}
const enum environmentvariablevalue_statecode {
"Active" = 0,
"Inactive" = 1,
}
const enum environmentvariablevalue_statuscode {
"Active" = 1,
"Inactive" = 2,
}
const enum mprpa_dqcaseactivity_mprpa_activitytype {
"Comment" = 557440000,
"Assignment" = 557440001,
"Status Change" = 557440002,
"Evidence Request" = 557440003,
"Approval" = 557440004,
"Escalation" = 557440005,
"Reopen" = 557440006,
}
const enum mprpa_dqcaseactivity_mprpa_systemgenerated {
"No" = 0,
"Yes" = 1,
}
const enum mprpa_dqcaseactivity_statecode {
"Activo" = 0,
"Inactivo" = 1,
}
const enum mprpa_dqcaseactivity_statuscode {
"Activo" = 1,
"Inactivo" = 2,
}
const enum mprpa_dqcaseevidence_mprpa_evidencetype {
"File" = 557440000,
"Link" = 557440001,
"Screenshot" = 557440002,
"Data Reference" = 557440003,
}
const enum mprpa_dqcaseevidence_mprpa_supportsclosure {
"No" = 0,
"Yes" = 1,
}
const enum mprpa_dqcaseevidence_statecode {
"Activo" = 0,
"Inactivo" = 1,
}
const enum mprpa_dqcaseevidence_statuscode {
"Activo" = 1,
"Inactivo" = 2,
}
const enum mprpa_dqexceptionreference_mprpa_operationalseverity {
"Critical" = 557440000,
"High" = 557440001,
"Medium" = 557440002,
"Low" = 557440003,
}
const enum mprpa_dqexceptionreference_statecode {
"Activo" = 0,
"Inactivo" = 1,
}
const enum mprpa_dqexceptionreference_statuscode {
"Activo" = 1,
"Inactivo" = 2,
}
const enum mprpa_dqremediationcase_mprpa_approvaloutcome {
"Pending" = 557440000,
"Approved" = 557440001,
"Rejected" = 557440002,
}
const enum mprpa_dqremediationcase_mprpa_evidencecomplete {
"No" = 0,
"Yes" = 1,
}
const enum mprpa_dqremediationcase_mprpa_resolutiontype {
"Corrected" = 557440000,
"Not an Issue" = 557440001,
"Waived" = 557440002,
}
const enum mprpa_dqremediationcase_mprpa_sourcecorrectionstate {
"Not Checked" = 557440000,
"Still Failing" = 557440001,
"Confirmed Later" = 557440002,
}
const enum mprpa_dqremediationcase_statecode {
"Activo" = 0,
"Inactivo" = 1,
}
const enum mprpa_dqremediationcase_statuscode {
"Activo" = 1,
"Inactivo" = 2,
}
const enum mprpa_dqstatus_mprpa_available {
"No" = 0,
"Yes" = 1,
}
const enum mprpa_dqstatus_mprpa_initial {
"No" = 0,
"Yes" = 1,
}
const enum mprpa_dqstatus_mprpa_requiresapproval {
"No" = 0,
"Yes" = 1,
}
const enum mprpa_dqstatus_mprpa_requirescomment {
"No" = 0,
"Yes" = 1,
}
const enum mprpa_dqstatus_mprpa_requiresevidence {
"No" = 0,
"Yes" = 1,
}
const enum mprpa_dqstatus_mprpa_terminal {
"No" = 0,
"Yes" = 1,
}
const enum mprpa_dqstatus_statecode {
"Activo" = 0,
"Inactivo" = 1,
}
const enum mprpa_dqstatus_statuscode {
"Activo" = 1,
"Inactivo" = 2,
}

export interface UxAgentDataApi extends BaseUxAgentDataApi<TableRegistrations, EnumRegistrations> {}

export interface GeneratedComponentProps {
    dataApi: UxAgentDataApi;
}

