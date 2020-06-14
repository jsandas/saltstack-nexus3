"""
File contains the groovy scripts used by Nexus 3 script api as objects 
that may be used in the nexus3 state module.
I put these here as it made it easy to sync the groovy with the module itself
"""

create_blobstore = """
import groovy.json.JsonSlurper

parsed_args = new JsonSlurper().parseText(args)

existingBlobStore = blobStore.getBlobStoreManager().get(parsed_args.name)
if (existingBlobStore == null) {
  if (parsed_args.type == "S3") {
      blobStore.createS3BlobStore(parsed_args.name, parsed_args.config)
      msg = "S3 blobstore {} created"
  } else {
      blobStore.createFileBlobStore(parsed_args.name, parsed_args.path)
      msg = "Created blobstore {} created"
  }
  log.info(msg, parsed_args.name)
} else {
    msg = "Blobstore {} already exists. Left untouched"
}

log.info(msg, parsed_args.name)
"""

create_content_selector = """
import groovy.json.JsonSlurper
import org.sonatype.nexus.selector.SelectorManager
import org.sonatype.nexus.selector.SelectorConfiguration

parsed_args = new JsonSlurper().parseText(args)

selectorManager = container.lookup(SelectorManager.class.name)

def selectorConfig
boolean update = true

selectorConfig = selectorManager.browse().find { it -> it.name == parsed_args.name } 

if (selectorConfig == null) {
    update = false
    selectorConfig = new SelectorConfiguration(
        'name': parsed_args.name
    )
}

selectorConfig.setDescription(parsed_args.description)
selectorConfig.setType('csel')
selectorConfig.setAttributes([
    'expression': parsed_args.search_expression
] as Map<String, Object>)

if (update) {
    selectorManager.update(selectorConfig)
} else {
    selectorManager.create(selectorConfig)
}
"""

create_repo_group = """
import groovy.json.JsonSlurper
import org.sonatype.nexus.repository.config.Configuration

parsed_args = new JsonSlurper().parseText(args)

repositoryManager = repository.repositoryManager

existingRepository = repositoryManager.get(parsed_args.name)

if (existingRepository != null) {

    newConfig = existingRepository.configuration.copy()
    // We only update values we are allowed to change (cf. greyed out options in gui)
    if (parsed_args.recipe_name == 'docker-group') {
        newConfig.attributes['docker']['forceBasicAuth'] = parsed_args.docker_force_basic_auth
        newConfig.attributes['docker']['v1Enabled'] = parsed_args.docker_v1_enabled
        newConfig.attributes['docker']['httpPort'] = parsed_args.http_port
    }
    newConfig.attributes['group']['memberNames'] = parsed_args.member_repos
    newConfig.attributes['storage']['strictContentTypeValidation'] = Boolean.valueOf(parsed_args.strict_content_validation)

    repositoryManager.update(newConfig)

} else {

    if (parsed_args.recipe_name == 'docker-group') {
        configuration = new Configuration(
                repositoryName: parsed_args.name,
                recipeName: parsed_args.recipe_name,
                online: true,
                attributes: [
                        docker: [
                                forceBasicAuth: parsed_args.docker_force_basic_auth,
                                v1Enabled : parsed_args.docker_v1_enabled,
                                httpPort: parsed_args.docker_http_port
                        ],
                        group: [
                                memberNames: parsed_args.member_repos
                        ],
                        storage: [
                                blobStoreName: parsed_args.blob_store,
                                strictContentTypeValidation: Boolean.valueOf(parsed_args.strict_content_validation)
                        ]
                ]
        )
    } else {
        configuration = new Configuration(
                repositoryName: parsed_args.name,
                recipeName: parsed_args.recipe_name,
                online: true,
                attributes: [
                        group  : [
                                memberNames: parsed_args.member_repos
                        ],
                        storage: [
                                blobStoreName: parsed_args.blob_store,
                                strictContentTypeValidation: Boolean.valueOf(parsed_args.strict_content_validation)
                        ]
                ]
        )
    }

    repositoryManager.create(configuration)

}
"""

create_repo_hosted = """
import groovy.json.JsonSlurper
import org.sonatype.nexus.repository.config.Configuration

parsed_args = new JsonSlurper().parseText(args)

repositoryManager = repository.repositoryManager

existingRepository = repositoryManager.get(parsed_args.name)

msg = "Args: {}"
log.debug(msg, args)

if (existingRepository != null) {

    msg = "Repo {} already exists.  Updating..."
    log.debug(msg, parsed_args.name)

    newConfig = existingRepository.configuration.copy()
    // We only update values we are allowed to change (cf. greyed out options in gui)
    if (parsed_args.recipe_name == 'docker-hosted') {
        newConfig.attributes['docker']['forceBasicAuth'] = parsed_args.docker_force_basic_auth
        newConfig.attributes['docker']['v1Enabled'] = parsed_args.docker_v1_enabled
         newConfig.attributes['docker']['httpPort'] = parsed_args.docker_http_port
    } else if (parsed_args.recipe_name == 'maven2-hosted') {
        newConfig.attributes['maven']['versionPolicy'] = parsed_args.maven_version_policy.toUpperCase()
        newConfig.attributes['maven']['layoutPolicy'] = parsed_args.maven_layout_policy.toUpperCase()
    } else if (parsed_args.recipe_name == 'yum-hosted') {
        newConfig.attributes['yum']['repodataDepth'] = parsed_args.yum_repodata_depth as Integer
        newConfig.attributes['yum']['deployPolicy'] = parsed_args.yum_deploy_policy.toUpperCase()
    }

    newConfig.attributes['storage']['writePolicy'] = parsed_args.write_policy.toUpperCase()
    newConfig.attributes['storage']['strictContentTypeValidation'] = Boolean.valueOf(parsed_args.strict_content_validation)

    repositoryManager.update(newConfig)

} else {

    if (parsed_args.recipe_name == 'maven2-hosted') {
        configuration = new Configuration(
                repositoryName: parsed_args.name,
                recipeName: parsed_args.recipe_name,
                online: true,
                attributes: [
                        maven: [
                                versionPolicy: parsed_args.maven_version_policy.toUpperCase(),
                                layoutPolicy : parsed_args.maven_layout_policy.toUpperCase()
                        ],
                        storage: [
                                writePolicy: parsed_args.write_policy.toUpperCase(),
                                blobStoreName: parsed_args.blob_store,
                                strictContentTypeValidation: Boolean.valueOf(parsed_args.strict_content_validation)
                        ]
                ]
        )
    } else if (parsed_args.recipe_name == 'docker-hosted') {
        configuration = new Configuration(
                repositoryName: parsed_args.name,
                recipeName: parsed_args.recipe_name,
                online: true,
                attributes: [
                        docker: [
                                forceBasicAuth: parsed_args.docker_force_basic_auth,
                                v1Enabled : parsed_args.docker_v1_enabled,
                                httpPort: parsed_args.docker_http_port
                        ],
                        storage: [
                                writePolicy: parsed_args.write_policy.toUpperCase(),
                                blobStoreName: parsed_args.blob_store,
                                strictContentTypeValidation: Boolean.valueOf(parsed_args.strict_content_validation)
                        ]
                ]
        )
    } else if (parsed_args.recipe_name == 'yum-hosted') {
        configuration = new Configuration(
                repositoryName: parsed_args.name,
                recipeName: parsed_args.recipe_name,
                online: true,
                attributes: [
                        yum  : [
                                repodataDepth : parsed_args.yum_repodata_depth.toInteger(),
                                deployPolicy : parsed_args.yum_deploy_policy.toUpperCase()
                        ],
                        storage: [
                                writePolicy: parsed_args.write_policy.toUpperCase(),
                                blobStoreName: parsed_args.blob_store,
                                strictContentTypeValidation: Boolean.valueOf(parsed_args.strict_content_validation)
                        ]
                ]
        )
    } else {       
        configuration = new Configuration(
                repositoryName: parsed_args.name,
                recipeName: parsed_args.recipe_name,
                online: true,
                attributes: [
                        storage: [
                                writePolicy: parsed_args.write_policy.toUpperCase(),
                                blobStoreName: parsed_args.blob_store,
                                strictContentTypeValidation: Boolean.valueOf(parsed_args.strict_content_validation)
                        ]
                ]
        )
    }

    msg = "Configuration: {}"
    log.debug(msg, configuration)

    repositoryManager.create(configuration)

}
"""

create_repo_proxy = """
import groovy.json.JsonSlurper
import org.sonatype.nexus.repository.config.Configuration

parsed_args = new JsonSlurper().parseText(args)

repositoryManager = repository.repositoryManager

authentication = parsed_args.remote_username == null ? null : [
        type: 'username',
        username: parsed_args.remote_username,
        password: parsed_args.remote_password
]

existingRepository = repositoryManager.get(parsed_args.name)

msg = "Args: {}"
log.debug(msg, args)

if (existingRepository != null) {

    msg = "Repo {} already exists.  Updating..."
    log.debug(msg, parsed_args.name)

    newConfig = existingRepository.configuration.copy()
    // We only update values we are allowed to change (cf. greyed out options in gui)
    if (parsed_args.recipe_name == 'docker-proxy') {
        newConfig.attributes['docker']['forceBasicAuth'] = parsed_args.docker_force_basic_auth
        newConfig.attributes['docker']['v1Enabled'] = parsed_args.docker_v1_enabled
        newConfig.attributes['dockerProxy']['indexType'] = parsed_args.docker_index_type
        newConfig.attributes['dockerProxy']['useTrustStoreForIndexAccess'] = parsed_args.docker_use_nexus_certificates_to_access_index
        newConfig.attributes['docker']['httpPort'] = parsed_args.docker_http_port
    } else if (parsed_args.recipe_name == 'maven2-proxy') {
        newConfig.attributes['maven']['versionPolicy'] = parsed_args.maven_version_policy.toUpperCase()
        newConfig.attributes['maven']['layoutPolicy'] = parsed_args.maven_layout_policy.toUpperCase()
    }

    newConfig.attributes['proxy']['remoteUrl'] = parsed_args.remote_url
    newConfig.attributes['proxy']['contentMaxAge'] = parsed_args.get('content_max_age', 1440.0)
    newConfig.attributes['proxy']['metadataMaxAge'] = parsed_args.get('metadata_max_age', 1440.0)
    newConfig.attributes['storage']['strictContentTypeValidation'] = Boolean.valueOf(parsed_args.strict_content_validation)
    newConfig.attributes['httpclient']['authentication'] = authentication

    repositoryManager.update(newConfig)

} else {

    if (parsed_args.recipe_name == 'bower-proxy') {
        configuration = new Configuration(
                repositoryName: parsed_args.name,
                recipeName: parsed_args.recipe_name,
                online: true,
                attributes: [
                        bower: [
                                rewritePackageUrls: true
                        ],
                        proxy: [
                                remoteUrl: parsed_args.remote_url,
                                contentMaxAge: parsed_args.get('content_max_age', 1440.0),
                                metadataMaxAge: parsed_args.get('metadata_max_age', 1440.0)
                        ],
                        httpclient: [
                                blocked: false,
                                autoBlock: true,
                                authentication: authentication
                        ],
                        storage: [
                                blobStoreName: parsed_args.blob_store,
                                strictContentTypeValidation: Boolean.valueOf(parsed_args.strict_content_validation)
                        ],
                        negativeCache: [
                                enabled: parsed_args.get("negative_cache_enabled", true),
                                timeToLive: parsed_args.get("negative_cache_ttl", 1440.0)
                        ]
                ]
        )
    } else if (parsed_args.recipe_name == 'maven2-proxy') {
        configuration = new Configuration(
                repositoryName: parsed_args.name,
                recipeName: parsed_args.recipe_name,
                online: true,
                attributes: [
                        maven  : [
                                versionPolicy: parsed_args.maven_version_policy.toUpperCase(),
                                layoutPolicy : parsed_args.maven_layout_policy.toUpperCase()
                        ],
                        proxy: [
                                remoteUrl: parsed_args.remote_url,
                                contentMaxAge: parsed_args.get('content_max_age', 1440.0),
                                metadataMaxAge: parsed_args.get('metadata_max_age', 1440.0)
                        ],
                        httpclient: [
                                blocked: false,
                                autoBlock: true,
                                authentication: authentication
                        ],
                        storage: [
                                blobStoreName: parsed_args.blob_store,
                                strictContentTypeValidation: Boolean.valueOf(parsed_args.strict_content_validation)
                        ],
                        negativeCache: [
                                enabled: parsed_args.get("negative_cache_enabled", true),
                                timeToLive: parsed_args.get("negative_cache_ttl", 1440.0)
                        ]
                ]
        )
    } else if (parsed_args.recipe_name == 'docker-proxy') {
        configuration = new Configuration(
                repositoryName: parsed_args.name,
                recipeName: parsed_args.recipe_name,
                online: true,
                attributes: [
                        docker: [
                                forceBasicAuth: parsed_args.docker_force_basic_auth,
                                v1Enabled : parsed_args.docker_v1_enabled,
                                httpPort: parsed_args.docker_http_port
                        ],
                        proxy: [
                                remoteUrl: parsed_args.remote_url,
                                contentMaxAge: parsed_args.get('content_max_age', 1440.0),
                                metadataMaxAge: parsed_args.get('metadata_max_age', 1440.0)
                        ],
                        dockerProxy: [
                                indexType: parsed_args.docker_index_type.toUpperCase(),
                                useTrustStoreForIndexAccess: parsed_args.docker_use_nexus_certificates_to_access_index
                        ],
                        httpclient: [
                                blocked: false,
                                autoBlock: true,
                                authentication: authentication
                        ],
                        storage: [
                                blobStoreName: parsed_args.blob_store,
                                strictContentTypeValidation: Boolean.valueOf(parsed_args.strict_content_validation)
                        ],
                        negativeCache: [
                                enabled: parsed_args.get("negative_cache_enabled", true),
                                timeToLive: parsed_args.get("negative_cache_ttl", 1440.0)
                        ]
                ]
        )
    } else {
        configuration = new Configuration(
                repositoryName: parsed_args.name,
                recipeName: parsed_args.recipe_name,
                online: true,
                attributes: [
                        proxy: [
                                remoteUrl: parsed_args.remote_url,
                                contentMaxAge: parsed_args.get('content_max_age', 1440.0),
                                metadataMaxAge: parsed_args.get('metadata_max_age', 1440.0)
                        ],
                        httpclient: [
                                blocked: false,
                                autoBlock: true,
                                authentication: authentication
                        ],
                        storage: [
                                blobStoreName: parsed_args.blob_store,
                                strictContentTypeValidation: Boolean.valueOf(parsed_args.strict_content_validation)
                        ],
                        negativeCache: [
                                enabled: parsed_args.get("negative_cache_enabled", true),
                                timeToLive: parsed_args.get("negative_cache_ttl", 1440.0)
                        ]
                ]
        )
    }

    msg = "Configuration: {}"
    log.debug(msg, configuration)

    repositoryManager.create(configuration)

}
"""

create_task = """
import groovy.json.JsonSlurper
import org.sonatype.nexus.scheduling.TaskConfiguration
import org.sonatype.nexus.scheduling.TaskInfo
import org.sonatype.nexus.scheduling.TaskScheduler
import org.sonatype.nexus.scheduling.schedule.Schedule

parsed_args = new JsonSlurper().parseText(args)

TaskScheduler taskScheduler = container.lookup(TaskScheduler.class.getName())

TaskInfo existingTask = taskScheduler.listsTasks().find { TaskInfo taskInfo ->
    taskInfo.name == parsed_args.name
}

if (existingTask && existingTask.getCurrentState().getRunState() != null) {
    log.info("Could not update currently running task : " + parsed_args.name)
    return
}

TaskConfiguration taskConfiguration = taskScheduler.createTaskConfigurationInstance(parsed_args.typeId)
if (existingTask) { taskConfiguration.setId(existingTask.getId()) }
taskConfiguration.setName(parsed_args.name)

parsed_args.taskProperties.each { key, value -> taskConfiguration.setString(key, value) }

if (parsed_args.task_alert_email) {
    taskConfiguration.setAlertEmail(parsed_args.task_alert_email)
}

parsed_args.booleanTaskProperties.each { key, value -> taskConfiguration.setBoolean(key, Boolean.valueOf(value)) }

Schedule schedule = taskScheduler.scheduleFactory.cron(new Date(), parsed_args.cron)

taskScheduler.scheduleTask(taskConfiguration, schedule)
"""

delete_blobstore = """
import groovy.json.JsonSlurper

parsed_args = new JsonSlurper().parseText(args)

existingBlobStore = blobStore.getBlobStoreManager().get(parsed_args.name)
if (existingBlobStore != null) {
    blobStore.getBlobStoreManager().delete(parsed_args.name)
}
"""

delete_repo = """
import groovy.json.JsonSlurper

parsed_args = new JsonSlurper().parseText(args)

repository.getRepositoryManager().delete(parsed_args.name)
"""

setup_anonymous_access = """
import groovy.json.JsonSlurper

parsed_args = new JsonSlurper().parseText(args)

security.setAnonymousAccess(Boolean.valueOf(parsed_args.anonymous_access))
"""

setup_base_url = """
import groovy.json.JsonSlurper

parsed_args = new JsonSlurper().parseText(args)

core.baseUrl(parsed_args.base_url)
"""

setup_capability = """
import groovy.json.JsonSlurper
import org.sonatype.nexus.capability.CapabilityReference
import org.sonatype.nexus.capability.CapabilityType
import org.sonatype.nexus.internal.capability.DefaultCapabilityReference
import org.sonatype.nexus.internal.capability.DefaultCapabilityRegistry

parsed_args = new JsonSlurper().parseText(args)

parsed_args.capability_properties['headerEnabled'] = parsed_args.capability_properties['headerEnabled'].toString()
parsed_args.capability_properties['footerEnabled'] = parsed_args.capability_properties['footerEnabled'].toString()

def capabilityRegistry = container.lookup(DefaultCapabilityRegistry.class.getName())
def capabilityType = CapabilityType.capabilityType(parsed_args.capability_typeId)

DefaultCapabilityReference existing = capabilityRegistry.all.find { CapabilityReference capabilityReference ->
    capabilityReference.context().descriptor().type() == capabilityType
}

if (existing) {
    log.info(parsed_args.typeId + ' capability updated to: {}',
            capabilityRegistry.update(existing.id(), Boolean.valueOf(parsed_args.get('capability_enabled', true)), existing.notes(), parsed_args.capability_properties).toString()
    )
}
else {
    log.info(parsed_args.typeId + ' capability created as: {}', capabilityRegistry.
            add(capabilityType, Boolean.valueOf(parsed_args.get('capability_enabled', true)), 'configured through api', parsed_args.capability_properties).toString()
    )
}
"""

setup_email = """
import groovy.json.JsonSlurper
import org.sonatype.nexus.email.EmailConfiguration
import org.sonatype.nexus.email.EmailManager

parsed_args = new JsonSlurper().parseText(args)

def emailMgr = container.lookup(EmailManager.class.getName());

emailConfig = new EmailConfiguration(
        enabled: parsed_args.email_server_enabled,
        host: parsed_args.email_server_host,
        port: Integer.valueOf(parsed_args.email_server_port),
        username: parsed_args.email_server_username,
        password: parsed_args.email_server_password,
        fromAddress: parsed_args.email_from_address,
        subjectPrefix: parsed_args.email_subject_prefix,
        startTlsEnabled: parsed_args.email_tls_enabled,
        startTlsRequired: parsed_args.email_tls_required,
        sslOnConnectEnabled: parsed_args.email_ssl_on_connect_enabled,
        sslCheckServerIdentityEnabled: parsed_args.email_ssl_check_server_identity_enabled,
        nexusTrustStoreEnabled: parsed_args.email_trust_store_enabled
)

emailMgr.configuration = emailConfig
"""

setup_http_proxy = """
import groovy.json.JsonSlurper

parsed_args = new JsonSlurper().parseText(args)


core.removeHTTPProxy()
if (parsed_args.with_http_proxy) {
    if (parsed_args.http_proxy_username) {
        core.httpProxyWithBasicAuth(parsed_args.http_proxy_host, parsed_args.http_proxy_port as int, parsed_args.http_proxy_username, parsed_args.http_proxy_password)
    } else {
        core.httpProxy(parsed_args.http_proxy_host, parsed_args.http_proxy_port as int)
    }
}

core.removeHTTPSProxy()
if (parsed_args.with_https_proxy) {
    if (parsed_args.https_proxy_username) {
        core.httpsProxyWithBasicAuth(parsed_args.https_proxy_host, parsed_args.https_proxy_port as int, parsed_args.https_proxy_username, parsed_args.https_proxy_password)
    } else {
        core.httpsProxy(parsed_args.https_proxy_host, parsed_args.https_proxy_port as int)
    }
}

if (parsed_args.with_http_proxy || parsed_args.with_https_proxy) {
    core.nonProxyHosts()
    core.nonProxyHosts(parsed_args.proxy_exclude_hosts as String[])
}
"""

setup_ldap = """
import org.sonatype.nexus.ldap.persist.LdapConfigurationManager
import org.sonatype.nexus.ldap.persist.entity.LdapConfiguration
import org.sonatype.nexus.ldap.persist.entity.Connection
import org.sonatype.nexus.ldap.persist.entity.Mapping
import groovy.json.JsonSlurper

parsed_args = new JsonSlurper().parseText(args)


def ldapConfigMgr = container.lookup(LdapConfigurationManager.class.getName());

def ldapConfig = new LdapConfiguration()
boolean update = false;

// Look for existing config to update
ldapConfigMgr.listLdapServerConfigurations().each {
    if (it.name == parsed_args.name) {
        ldapConfig = it
        update = true
    }
}

ldapConfig.setName(parsed_args.name)

// Connection
connection = new Connection()
connection.setHost(new Connection.Host(Connection.Protocol.valueOf(parsed_args.protocol), parsed_args.hostname, Integer.valueOf(parsed_args.port)))
if (parsed_args.auth == "simple") {
    connection.setAuthScheme("simple")
    connection.setSystemUsername(parsed_args.username)
    connection.setSystemPassword(parsed_args.password)
} else {
    connection.setAuthScheme("none")
}
connection.setSearchBase(parsed_args.search_base)
connection.setConnectionTimeout(30)
connection.setConnectionRetryDelay(300)
connection.setMaxIncidentsCount(3)
ldapConfig.setConnection(connection)


// Mapping
mapping = new Mapping()
mapping.setUserBaseDn(parsed_args.user_base_dn)
mapping.setLdapFilter(parsed_args.user_ldap_filter)
mapping.setUserObjectClass(parsed_args.user_object_class)
mapping.setUserIdAttribute(parsed_args.user_id_attribute)
mapping.setUserRealNameAttribute(parsed_args.user_real_name_attribute)
mapping.setEmailAddressAttribute(parsed_args.user_email_attribute)

if (parsed_args.map_groups_as_roles) {
    if(parsed_args.map_groups_as_roles_type == "static"){
        mapping.setLdapGroupsAsRoles(true)
        mapping.setGroupBaseDn(parsed_args.group_base_dn)
        mapping.setGroupObjectClass(parsed_args.group_object_class)
        mapping.setGroupIdAttribute(parsed_args.group_id_attribute)
        mapping.setGroupMemberAttribute(parsed_args.group_member_attribute)
        mapping.setGroupMemberFormat(parsed_args.group_member_format)
    } else if (parsed_args.map_groups_as_roles_type == "dynamic") {
        mapping.setLdapGroupsAsRoles(true)
        mapping.setUserMemberOfAttribute(parsed_args.user_memberof_attribute)
    }
}

mapping.setUserSubtree(parsed_args.user_subtree)
mapping.setGroupSubtree(parsed_args.group_subtree)

ldapConfig.setMapping(mapping)


if (update) {
    ldapConfigMgr.updateLdapServerConfiguration(ldapConfig)
} else {
    ldapConfigMgr.addLdapServerConfiguration(ldapConfig)
}
"""

setup_privilege = """
import groovy.json.JsonSlurper
import org.sonatype.nexus.security.privilege.NoSuchPrivilegeException
import org.sonatype.nexus.security.user.UserManager
import org.sonatype.nexus.security.privilege.Privilege

parsed_args = new JsonSlurper().parseText(args)

authManager = security.getSecuritySystem().getAuthorizationManager(UserManager.DEFAULT_SOURCE)

def privilege
boolean update = true

try {
    privilege = authManager.getPrivilege(parsed_args.name)
} catch (NoSuchPrivilegeException ignored) {
    // could not find any existing  privilege
    update = false
    privilege = new Privilege(
            'id': parsed_args.name,
            'name': parsed_args.name
    )
}

privilege.setDescription(parsed_args.description)
privilege.setType(parsed_args.type)
privilege.setProperties([
        'format': parsed_args.format,
        'contentSelector': parsed_args.contentSelector,
        'repository': parsed_args.repository,
        'actions': parsed_args.actions.join(',')
] as Map<String, String>)

if (update) {
    authManager.updatePrivilege(privilege)
    log.info("Privilege {} updated", parsed_args.name)
} else {
    authManager.addPrivilege(privilege)
    log.info("Privilege {} created", parsed_args.name)
}
"""

setup_realms = """
import groovy.json.JsonSlurper
import org.sonatype.nexus.security.realm.RealmManager

parsed_args = new JsonSlurper().parseText(args)

realmManager = container.lookup(RealmManager.class.getName())

if (parsed_args.realm_name == 'NuGetApiKey') {
    // enable/disable the NuGet API-Key Realm
    realmManager.enableRealm("NuGetApiKey", parsed_args.status)
}

if (parsed_args.realm_name == 'NpmToken') {
    // enable/disable the npm Bearer Token Realm
    realmManager.enableRealm("NpmToken", parsed_args.status)
}

if (parsed_args.realm_name == 'rutauth-realm') {
    // enable/disable the Rut Auth Realm
    realmManager.enableRealm("rutauth-realm", parsed_args.status)
}

if (parsed_args.realm_name == 'LdapRealm') {
    // enable/disable the LDAP Realm
    realmManager.enableRealm("LdapRealm", parsed_args.status)
}

if (parsed_args.realm_name == 'DockerToken') {
    // enable/disable the Docker Bearer Token Realm
    realmManager.enableRealm("DockerToken", parsed_args.status)
}
"""

setup_role = """
import groovy.json.JsonSlurper
import org.sonatype.nexus.security.user.UserManager
import org.sonatype.nexus.security.role.NoSuchRoleException

parsed_args = new JsonSlurper().parseText(args)

authManager = security.getSecuritySystem().getAuthorizationManager(UserManager.DEFAULT_SOURCE)

privileges = (parsed_args.privileges == null ? new HashSet() : parsed_args.privileges.toSet())
roles = (parsed_args.roles == null ? new HashSet() : parsed_args.roles.toSet())

try {
    existingRole = authManager.getRole(parsed_args.id)
    existingRole.setName(parsed_args.name)
    existingRole.setDescription(parsed_args.description)
    existingRole.setPrivileges(privileges)
    existingRole.setRoles(roles)
    authManager.updateRole(existingRole)
    log.info("Role {} updated", parsed_args.name)
} catch (NoSuchRoleException ignored) {
    security.addRole(parsed_args.id, parsed_args.name, parsed_args.description, privileges.toList(), roles.toList())
    log.info("Role {} created", parsed_args.name)
}
"""

setup_user = """
import groovy.json.JsonSlurper
import org.sonatype.nexus.security.user.UserManager
import org.sonatype.nexus.security.user.UserNotFoundException
import org.sonatype.nexus.security.user.User

parsed_args = new JsonSlurper().parseText(args)
state = parsed_args.state == null ? 'present' : parsed_args.state

if ( state == 'absent' ) {
    deleteUser(parsed_args)
} else {
    try {
        updateUser(parsed_args)
    } catch (UserNotFoundException ignored) {
        addUser(parsed_args)
    }
}

def updateUser(parsed_args) {
    User user = security.securitySystem.getUser(parsed_args.username)
    user.setFirstName(parsed_args.first_name)
    user.setLastName(parsed_args.last_name)
    user.setEmailAddress(parsed_args.email)
    security.securitySystem.updateUser(user)
    security.setUserRoles(parsed_args.username, parsed_args.roles)
    security.securitySystem.changePassword(parsed_args.username, parsed_args.password)
    log.info("Updated user {}", parsed_args.username)
}

def addUser(parsed_args) {
    security.addUser(parsed_args.username, parsed_args.first_name, parsed_args.last_name, parsed_args.email, true, parsed_args.password, parsed_args.roles)
    log.info("Created user {}", parsed_args.username)
}

def deleteUser(parsed_args) {
    try {
        security.securitySystem.deleteUser(parsed_args.username, UserManager.DEFAULT_SOURCE)
        log.info("Deleted user {}", parsed_args.username)
    } catch (UserNotFoundException ignored) {
        log.info("Delete user: user {} does not exist", parsed_args.username)
    }
}
"""

update_admin_password = """
import groovy.json.JsonSlurper

parsed_args = new JsonSlurper().parseText(args)

security.securitySystem.changePassword('admin', parsed_args.new_password)
"""
